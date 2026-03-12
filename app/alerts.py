from __future__ import annotations

import httpx


class TelegramAlerter:
    def __init__(self, token: str | None, chat_id: str | None):
        self.token = token
        self.chat_id = chat_id
        self.client = httpx.AsyncClient(timeout=8)

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    async def send(self, title: str, payload: dict):
        if not self.enabled:
            return
        txt = (
            f"*{title}*\n"
            f"{payload['symbol']} | {payload['setup']}\n"
            f"Entry: `{payload['entry']:.6f}` SL: `{payload['sl']:.6f}`\n"
            f"TP1: `{payload['tp1']:.6f}` TP2: `{payload['tp2']:.6f}`\n"
            f"Score: *{payload['score']:.1f}* | Conf: *{payload['confidence']:.1f}%*\n"
            f"Why: {', '.join(payload['reasons'])}"
        )
        await self.client.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={"chat_id": self.chat_id, "text": txt, "parse_mode": "Markdown"},
        )
