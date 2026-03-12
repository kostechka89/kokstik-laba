from __future__ import annotations

from typing import Any
import httpx


class MexcClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=10)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        r = await self.client.get(f"{self.base_url}{path}", params=params)
        r.raise_for_status()
        data = r.json()
        return data.get("data", data)

    async def symbols(self) -> list[dict]:
        return await self._get("/api/v1/contract/detail")

    async def ticker24h(self) -> list[dict]:
        return await self._get("/api/v1/contract/ticker")

    async def klines(self, symbol: str, interval: str = "Min1", limit: int = 80) -> list[list[float]]:
        return await self._get(f"/api/v1/contract/kline/{symbol}", {"interval": interval, "limit": limit})

    async def depth(self, symbol: str, limit: int = 20) -> dict:
        return await self._get(f"/api/v1/contract/depth/{symbol}", {"limit": limit})

    async def price(self, symbol: str) -> dict:
        return await self._get(f"/api/v1/contract/ticker/{symbol}")

    async def close(self):
        await self.client.aclose()
