from fastapi.testclient import TestClient

from user_service.main import app

client = TestClient(app)


def _register(username: str) -> dict[str, str]:
    body = {"username": username, "password": f"correct-horse-{username}"}
    client.post("/register", json=body)
    return body


def test_login_token_is_accepted_by_me():
    body = _register("alice")
    token = client.post("/login", json=body).json()["access_token"]
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.json() == {"username": "alice"}


def test_login_rejects_wrong_password():
    _register("bob")
    resp = client.post("/login", json={"username": "bob", "password": "wrong"})
    assert resp.status_code == 401


def test_register_rejects_taken_username():
    body = _register("carol")
    assert client.post("/register", json=body).status_code == 409


def test_me_rejects_malformed_token():
    resp = client.get("/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401
