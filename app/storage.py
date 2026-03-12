from __future__ import annotations

import aiosqlite
import json
from datetime import datetime, timezone


class Storage:
    def __init__(self, path: str = "signals.db"):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    setup TEXT NOT NULL,
                    score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    risk_tag TEXT NOT NULL,
                    entry REAL NOT NULL,
                    sl REAL NOT NULL,
                    tp1 REAL NOT NULL,
                    tp2 REAL NOT NULL,
                    ttl_expires_at TEXT NOT NULL,
                    reasons TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    outcome TEXT DEFAULT 'NONE',
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def insert_signal(self, signal: dict):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO signals(symbol,setup,score,confidence,risk_tag,entry,sl,tp1,tp2,ttl_expires_at,reasons,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    signal["symbol"], signal["setup"], signal["score"], signal["confidence"], signal["risk_tag"], signal["entry"],
                    signal["sl"], signal["tp1"], signal["tp2"], signal["ttl_expires_at"], json.dumps(signal["reasons"]),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            await db.commit()

    async def top_active(self, limit: int = 10) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM signals WHERE status='ACTIVE' ORDER BY score DESC, confidence DESC LIMIT ?", (limit,)
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def recent(self, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM signals ORDER BY id DESC LIMIT ?", (limit,))
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def active_for_symbol_setup(self, symbol: str, setup: str) -> dict | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM signals WHERE symbol=? AND setup=? AND status='ACTIVE' ORDER BY id DESC LIMIT 1", (symbol, setup)
            )
            row = await cur.fetchone()
            return dict(row) if row else None
