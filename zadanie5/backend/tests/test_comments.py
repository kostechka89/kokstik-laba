from __future__ import annotations

from tests.utils import auth_headers, login, register


def _create_news(client, tokens) -> int:
    resp = client.post(
        "/news/",
        headers=auth_headers(tokens),
        json={"title": "N", "content": {"text": "t"}},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_comments_read_public_and_create_requires_auth(client):
    register(client, "author@example.com", "pass", verified=True)
    atok = login(client, "author@example.com", "pass")
    news_id = _create_news(client, atok)

    r = client.get(f"/comments/?news_id={news_id}")
    assert r.status_code == 200

    c = client.post("/comments/", json={"news_id": news_id, "text": "hi"})
    assert c.status_code == 401


def test_comment_author_can_update_and_delete_own_comment(client):
    register(client, "author2@example.com", "pass", verified=True)
    atok = login(client, "author2@example.com", "pass")
    news_id = _create_news(client, atok)

    register(client, "commenter@example.com", "pass")
    ctok = login(client, "commenter@example.com", "pass")
    created = client.post(
        "/comments/",
        headers=auth_headers(ctok),
        json={"news_id": news_id, "text": "first"},
    )
    assert created.status_code == 200
    cid = created.json()["id"]

    updated = client.patch(
        f"/comments/{cid}",
        headers=auth_headers(ctok),
        json={"text": "updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["text"] == "updated"

    deleted = client.delete(f"/comments/{cid}", headers=auth_headers(ctok))
    assert deleted.status_code == 200


def test_admin_can_delete_foreign_comment(client):
    register(client, "author3@example.com", "pass", verified=True)
    atok = login(client, "author3@example.com", "pass")
    news_id = _create_news(client, atok)

    register(client, "commenter2@example.com", "pass")
    ctok = login(client, "commenter2@example.com", "pass")
    created = client.post(
        "/comments/",
        headers=auth_headers(ctok),
        json={"news_id": news_id, "text": "first"},
    )
    cid = created.json()["id"]

    register(client, "admin2@example.com", "pass", admin=True)
    atok2 = login(client, "admin2@example.com", "pass")
    deleted = client.delete(f"/comments/{cid}", headers=auth_headers(atok2))
    assert deleted.status_code == 200
