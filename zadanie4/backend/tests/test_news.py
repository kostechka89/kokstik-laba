from __future__ import annotations

from tests.utils import auth_headers, login, register


def test_news_list_is_public(client):
    resp = client.get("/news/")
    assert resp.status_code == 200


def test_author_can_create_update_delete_own_news(client):
    register(client, "author@example.com", "pass", verified=True)
    tokens = login(client, "author@example.com", "pass")

    created = client.post(
        "/news/",
        headers=auth_headers(tokens),
        json={"title": "Hello", "content": {"text": "one"}},
    )
    assert created.status_code == 200
    news_id = created.json()["id"]

    updated = client.patch(
        f"/news/{news_id}",
        headers=auth_headers(tokens),
        json={"title": "Updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"

    deleted = client.delete(f"/news/{news_id}", headers=auth_headers(tokens))
    assert deleted.status_code == 200
    gone = client.get(f"/news/{news_id}")
    assert gone.status_code == 404


def test_non_author_cannot_update_foreign_news_but_admin_can(client):
    register(client, "author2@example.com", "pass", verified=True)
    author_tokens = login(client, "author2@example.com", "pass")
    created = client.post(
        "/news/",
        headers=auth_headers(author_tokens),
        json={"title": "Hello", "content": {"text": "one"}},
    )
    news_id = created.json()["id"]

    register(client, "reader@example.com", "pass")
    reader_tokens = login(client, "reader@example.com", "pass")
    forbidden = client.patch(
        f"/news/{news_id}",
        headers=auth_headers(reader_tokens),
        json={"title": "Hack"},
    )
    assert forbidden.status_code == 403

    register(client, "admin@example.com", "pass", admin=True)
    admin_tokens = login(client, "admin@example.com", "pass")
    ok = client.patch(
        f"/news/{news_id}",
        headers=auth_headers(admin_tokens),
        json={"title": "Admin edit"},
    )
    assert ok.status_code == 200
    assert ok.json()["title"] == "Admin edit"
