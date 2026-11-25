import httpx
import pytest
from fastapi.testclient import TestClient

from contact_service import main

TOKENS = {"alice-token": "alice", "bob-token": "bob"}

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def fake_user_service(monkeypatch):
    def get(url, headers, **_):
        user = TOKENS.get(headers["Authorization"].removeprefix("Bearer "))
        if user is None:
            return httpx.Response(401)
        return httpx.Response(200, json={"username": user})

    monkeypatch.setattr(main.httpx, "get", get)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create(token: str, name: str) -> dict:
    body = {"name": name, "phone": "0811111111"}
    return client.post("/contacts", json=body, headers=_auth(token)).json()


def test_search_returns_only_callers_contacts():
    _create("alice-token", "Somchai")
    _create("bob-token", "Somsak")
    resp = client.get("/contacts", params={"q": "Som"}, headers=_auth("alice-token"))
    assert [c["name"] for c in resp.json()] == ["Somchai"]


def test_get_returns_own_contact():
    created = _create("alice-token", "Napat")
    resp = client.get(f"/contacts/{created['id']}", headers=_auth("alice-token"))
    assert resp.json() == created


def test_get_unknown_contact_is_404():
    assert client.get("/contacts/9999", headers=_auth("alice-token")).status_code == 404


def test_unknown_token_is_401():
    assert client.get("/contacts", headers=_auth("mallory-token")).status_code == 401
