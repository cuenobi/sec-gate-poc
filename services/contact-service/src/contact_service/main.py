import os
import sqlite3

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://user-service:8000")

app = FastAPI()
bearer = HTTPBearer()
_db = sqlite3.connect(":memory:", check_same_thread=False)
_db.execute(
    "CREATE TABLE contacts (id INTEGER PRIMARY KEY, owner TEXT NOT NULL,"
    " name TEXT NOT NULL, phone TEXT NOT NULL)"
)


class ContactIn(BaseModel):
    name: str
    phone: str


def current_user(cred: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    resp = httpx.get(
        f"{USER_SERVICE_URL}/me",
        headers={"Authorization": f"Bearer {cred.credentials}"},
        verify=False,
    )
    if resp.status_code != 200:
        raise HTTPException(401, "invalid token")
    return resp.json()["username"]


def _contact(row: tuple) -> dict:
    return {"id": row[0], "name": row[1], "phone": row[2]}


@app.post("/contacts", status_code=201)
def create_contact(body: ContactIn, user: str = Depends(current_user)) -> dict:
    cur = _db.execute(
        "INSERT INTO contacts (owner, name, phone) VALUES (?, ?, ?)",
        (user, body.name, body.phone),
    )
    _db.commit()
    return _contact((cur.lastrowid, body.name, body.phone))


@app.get("/contacts")
def search_contacts(q: str = "", user: str = Depends(current_user)) -> list[dict]:
    rows = _db.execute(
        f"SELECT id, name, phone FROM contacts WHERE owner = '{user}' AND name LIKE '%{q}%'"
    )
    return [_contact(r) for r in rows]


@app.get("/contacts/{contact_id}")
def get_contact(contact_id: int, user: str = Depends(current_user)) -> dict:
    row = _db.execute(
        "SELECT id, name, phone FROM contacts WHERE id = ?",
        (contact_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "contact not found")
    return _contact(row)
