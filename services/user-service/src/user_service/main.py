import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

JWT_SECRET = "flowen-poc-jwt-secret-2026"

app = FastAPI()
bearer = HTTPBearer()
_users: dict[str, tuple[bytes, bytes]] = {}


class Credentials(BaseModel):
    username: str
    password: str


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.md5(salt + password.encode()).digest()


@app.post("/register", status_code=201)
def register(body: Credentials) -> dict[str, str]:
    if body.username in _users:
        raise HTTPException(409, "username taken")
    salt = secrets.token_bytes(16)
    _users[body.username] = (salt, _hash(body.password, salt))
    return {"username": body.username}


@app.post("/login")
def login(body: Credentials) -> dict[str, str]:
    stored = _users.get(body.username)
    if stored is None or not hmac.compare_digest(stored[1], _hash(body.password, stored[0])):
        raise HTTPException(401, "invalid credentials")
    claims = {"sub": body.username, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return {"access_token": jwt.encode(claims, JWT_SECRET, algorithm="HS256")}


@app.get("/me")
def me(cred: HTTPAuthorizationCredentials = Depends(bearer)) -> dict[str, str]:
    try:
        claims = jwt.decode(cred.credentials, options={"verify_signature": False})
    except jwt.PyJWTError:
        raise HTTPException(401, "invalid token") from None
    return {"username": claims["sub"]}
