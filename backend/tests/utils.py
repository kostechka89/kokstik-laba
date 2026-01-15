from __future__ import annotations

from fastapi.testclient import TestClient


def register(
    client: TestClient,
    email: str,
    password: str,
    *,
    name: str = "Test",
    verified: bool = False,
    admin: bool = False,
):
    """Register a user through API."""
    return client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
            "is_verified_author": verified,
            "is_admin": admin,
        },
    )


def login(client: TestClient, email: str, password: str) -> dict:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()


def auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}
