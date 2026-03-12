from __future__ import annotations

import asyncio
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.alerts import TelegramAlerter
from app.config import PRESETS, settings
from app.engine import SignalEngine
from app.mexc_client import MexcClient
from app.storage import Storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="MEXC Pump Reversal Short Dashboard")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

storage = Storage(settings.db_path)
client = MexcClient(settings.mexc_base_url)
alerter = TelegramAlerter(settings.telegram_token, settings.telegram_chat_id)
engine = SignalEngine(client, storage, alerter)


class PresetUpdate(BaseModel):
    preset: str


@app.on_event("startup")
async def startup():
    await storage.init()
    asyncio.create_task(engine.loop())


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "presets": list(PRESETS.keys()), "preset": engine.state.preset})


@app.get("/api/dashboard")
async def dashboard_data():
    top = await storage.top_active(10)
    tracked = await storage.recent(40)
    for row in top:
        row["reasons"] = json.loads(row["reasons"]) if isinstance(row["reasons"], str) else row["reasons"]
    for row in tracked:
        row["reasons"] = json.loads(row["reasons"]) if isinstance(row["reasons"], str) else row["reasons"]
    return {
        "top_signals": top,
        "watchlist_near_trigger": engine.state.near_trigger[:20],
        "tracked": tracked,
        "regime": {
            "market_regime": engine.state.market_regime,
            "active_pumps": engine.state.active_pumps,
            "avg_volatility": engine.state.avg_volatility,
            "preset": engine.state.preset,
        },
        "scanner": {
            "last_scan_at": engine.state.last_scan_at,
            "last_error": engine.state.last_error,
            "scanned_symbols": engine.state.scanned_symbols,
            "liquid_symbols": engine.state.liquid_symbols,
            "ready_candidates": engine.state.ready_candidates,
            "scan_interval_sec": settings.scan_interval_sec,
        },
    }


@app.post("/api/preset")
async def set_preset(payload: PresetUpdate):
    if payload.preset not in PRESETS:
        return {"ok": False, "error": "unknown preset"}
    engine.set_preset(payload.preset)
    return {"ok": True, "preset": engine.state.preset}
