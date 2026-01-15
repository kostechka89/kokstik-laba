
def create_user(client, email, password, verified=False, admin=False):
    return client.post(
        "/auth/register",
        json={
            "name": "Test",
            "email": email,
            "password": password,
            "is_verified_author": verified,
            "is_admin": admin,
        },
    )


def login(client, email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()


def test_register_and_login(client):
    response = create_user(client, "user1@example.com", "pass")
    assert response.status_code == 200
    tokens = login(client, "user1@example.com", "pass")
    assert "access_token" in tokens


def test_unverified_cannot_create_news(client):
    create_user(client, "user2@example.com", "pass")
    tokens = login(client, "user2@example.com", "pass")
    response = client.post(
        "/news/",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"title": "News", "content": {"text": "hi"}},
    )
    assert response.status_code == 403


def test_verified_can_create_news(client):
    create_user(client, "user3@example.com", "pass", verified=True)
    tokens = login(client, "user3@example.com", "pass")
    response = client.post(
        "/news/",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"title": "News", "content": {"text": "hi"}},
    )
    assert response.status_code == 200
    news_id = response.json()["id"]
    fetched = client.get(f"/news/{news_id}")
    assert fetched.status_code == 200
