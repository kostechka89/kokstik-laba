from __future__ import annotations

from tests.utils import login


def test_login_wrong_password_returns_401(client, test_user):
    resp = client.post(
        "/auth/login",
        json={"email": test_user["email"], "password": "bad"},
    )
    assert resp.status_code == 401


def test_refresh_requires_existing_session(client, test_user):
    tokens = login(client, test_user["email"], test_user["password"])
    out = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert out.status_code == 200
    refreshed = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 401


def test_sessions_endpoint_lists_active_sessions(client, test_user):
    tokens = login(client, test_user["email"], test_user["password"])
    resp = client.get("/auth/sessions", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
