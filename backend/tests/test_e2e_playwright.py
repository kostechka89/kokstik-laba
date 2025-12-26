from __future__ import annotations

import os

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_E2E") != "1",
    reason="E2E requires running backend (8000) and frontend (5173). Set RUN_E2E=1 to enable.",
)


def test_e2e_news_flow():
    """Very small UI smoke: open homepage and check it renders."""
    from playwright.sync_api import sync_playwright

    base = os.getenv("FRONTEND_BASE", "http://localhost:5173")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base, wait_until="domcontentloaded")
        # We only check that the app shell is present.
        assert "News" in page.content() or "Новости" in page.content() or "LAB" in page.title()
        browser.close()
