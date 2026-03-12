from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
import asyncio
import math
import logging

from app.config import PRESETS, settings, Preset
from app.indicators import atr_pct, macd, rsi, safe_ret

logger = logging.getLogger(__name__)


@dataclass
class ScanState:
    preset: str = "BALANCED"
    market_regime: str = "NEUTRAL"
    active_pumps: int = 0
    avg_volatility: float = 0.0
    near_trigger: list[dict] = None

    def __post_init__(self):
        if self.near_trigger is None:
            self.near_trigger = []


class SignalEngine:
    def __init__(self, client, storage, alerter):
        self.client = client
        self.storage = storage
        self.alerter = alerter
        self.state = ScanState()
        self.cooldowns: dict[str, datetime] = {}

    def set_preset(self, preset: str):
        if preset in PRESETS:
            self.state.preset = preset

    def _score(self, p: Preset, ret5: float, ret15: float, rsi_val: float, vr: float, level_reject: float, momentum: float, liq: float):
        pump = min(20, max(0, (ret5 / p.ret5_min) * 10 + (ret15 / p.ret15_min) * 10))
        overheat = max(0, 18 - abs((p.rsi_min + p.rsi_max) / 2 - rsi_val) * 0.7)
        vol = min(16, vr / p.vr_min * 10)
        lvl = min(18, level_reject)
        mom = min(16, momentum)
        liq = min(12, liq)
        return max(0, min(100, pump + overheat + vol + lvl + mom + liq))

    async def scan_once(self):
        p = PRESETS[self.state.preset]
        try:
            contracts = await self.client.symbols()
            tickers = await self.client.ticker24h()
        except Exception as e:
            logger.warning("data fetch failed: %s", e)
            return

        tmap = {t.get("symbol"): t for t in tickers if t.get("symbol", "").endswith("_USDT")}
        liquid = []
        for c in contracts:
            sym = c.get("symbol")
            if sym not in tmap:
                continue
            last = float(tmap[sym].get("lastPrice", 0) or 0)
            vol = float(tmap[sym].get("amount24", 0) or 0)
            if last <= 0 or vol <= 0:
                continue
            if vol < settings.min_24h_volume_usdt or vol > settings.max_24h_volume_usdt or last > settings.max_price:
                continue
            liquid.append((sym, vol))
        liquid.sort(key=lambda x: x[1], reverse=True)
        symbols = [x[0] for x in liquid[: settings.pair_limit]]
        self.state.active_pumps = 0
        self.state.near_trigger = []
        vols = []

        for sym in symbols:
            signal = await self._analyze_symbol(sym, p)
            if not signal:
                continue
            vols.append(signal["atr_pct"])
            if signal["ret5"] > p.ret5_min or signal["ret15"] > p.ret15_min:
                self.state.active_pumps += 1
            if signal["status"] == "NEAR":
                self.state.near_trigger.append(signal)
                continue
            if signal["status"] != "READY":
                continue
            score = signal["score"]
            if score < p.score_min:
                continue

            cooldown_key = f"{sym}:{signal['setup']}"
            now = datetime.now(timezone.utc)
            if cooldown_key in self.cooldowns and self.cooldowns[cooldown_key] > now:
                continue
            existing = await self.storage.active_for_symbol_setup(sym, signal["setup"])
            if existing:
                continue
            payload = self._risk_pack(signal, p)
            await self.storage.insert_signal(payload)
            self.cooldowns[cooldown_key] = now + timedelta(minutes=settings.cooldown_minutes)
            await self.alerter.send("new signal", payload)

        self.state.avg_volatility = round(sum(vols) / len(vols), 3) if vols else 0
        self.state.market_regime = "RISK-OFF" if self.state.active_pumps > 8 else "RISK-ON" if self.state.active_pumps < 3 else "MIXED"

    async def _analyze_symbol(self, sym: str, p: Preset) -> dict | None:
        try:
            one = await self.client.klines(sym, "Min1", 80)
            five = await self.client.klines(sym, "Min5", 60)
            fifteen = await self.client.klines(sym, "Min15", 60)
            depth = await self.client.depth(sym, 20)
        except Exception:
            return None
        if len(one) < 40 or len(five) < 10 or len(fifteen) < 5:
            return None

        closes = [float(x[4]) for x in one]
        highs = [float(x[2]) for x in one]
        lows = [float(x[3]) for x in one]
        vols = [float(x[5]) for x in one]
        price = closes[-1]
        ret1 = safe_ret(closes[-1], closes[-2])
        ret3 = safe_ret(closes[-1], closes[-4])
        ret5 = safe_ret(closes[-1], closes[-6])
        ret15 = safe_ret(float(fifteen[-1][4]), float(fifteen[-2][4]))
        rsi_v = rsi(closes)
        macd_v = macd(closes)
        vol5 = sum(vols[-5:]) / 5
        vol20 = max(1e-9, sum(vols[-25:-5]) / 20)
        vr = vol5 / vol20
        local_high = max(highs[-30:])
        local_low = min(lows[-30:])
        dist_high = safe_ret(local_high, price) * -1
        dist_low = safe_ret(price, local_low)
        atr = atr_pct(highs, lows, closes)

        asks = depth.get("asks", []) if isinstance(depth, dict) else []
        bids = depth.get("bids", []) if isinstance(depth, dict) else []
        best_ask = float(asks[0][0]) if asks else price
        best_bid = float(bids[0][0]) if bids else price
        spread = (best_ask - best_bid) / price * 100 if price else 0
        ask_depth = sum(float(a[1]) for a in asks[:8]) if asks else 0
        bid_depth = sum(float(b[1]) for b in bids[:8]) if bids else 0
        liq_quality = max(0.0, 12 - spread * 250 + math.log1p(min(ask_depth, bid_depth)) * 2.5)

        if vr > settings.vr_max_filter or ret15 > settings.ret15_max_filter:
            return None

        overheat = p.rsi_min <= rsi_v <= p.rsi_max and vr >= p.vr_min
        failed_break = highs[-1] > local_high * 0.999 and closes[-1] < highs[-1] * 0.995
        confirm_down = closes[-1] < closes[-2]
        hist_turn = macd_v["hist_slope"] < 0
        level_reject_q = 18 if failed_break and confirm_down else 10 if confirm_down else 4
        momentum_q = 16 if hist_turn and confirm_down else 8 if (hist_turn or confirm_down) else 2

        near = (ret5 > p.ret5_min * 0.8 or ret15 > p.ret15_min * 0.8) and rsi_v > p.rsi_min * 0.95
        if not overheat and near:
            return {"symbol": sym, "status": "NEAR", "ret5": ret5, "ret15": ret15, "rsi": rsi_v, "vr": vr, "atr_pct": atr}
        if not (ret5 >= p.ret5_min or ret15 >= p.ret15_min):
            return None

        setup = "pump_reversal_short"
        if failed_break:
            setup = "false_breakout_short"
        elif confirm_down and abs(price - round(price)) / max(price, 1e-9) < 0.0025:
            setup = "level_reject_short"
        elif ret1 < -0.6 and overheat:
            setup = "knife_continuation_short"

        score = self._score(p, ret5, ret15, rsi_v, vr, level_reject_q, momentum_q, liq_quality)
        reasons = [
            f"ret5={ret5:.2f}% ret15={ret15:.2f}%",
            f"RSI={rsi_v:.1f}",
            f"VR={vr:.2f}",
            "failed breakout" if failed_break else "local high rejection",
            "MACD hist down" if hist_turn else "MACD flat/up",
        ]
        return {
            "symbol": sym,
            "setup": setup,
            "status": "READY",
            "ret1": ret1,
            "ret3": ret3,
            "ret5": ret5,
            "ret15": ret15,
            "rsi": rsi_v,
            "vr": vr,
            "macd": macd_v,
            "dist_high": dist_high,
            "dist_low": dist_low,
            "atr_pct": atr,
            "spread": spread,
            "score": score,
            "confidence": min(99.0, score),
            "reasons": reasons,
            "price": price,
            "high": local_high,
        }

    def _risk_pack(self, signal: dict, p: Preset) -> dict:
        entry = signal["price"]
        sl = max(signal["high"] * 1.0025, entry * 1.006)
        risk = sl - entry
        tp1 = entry - risk * 1.2
        tp2 = entry - risk * 2.0
        rr1 = (entry - tp1) / risk if risk else 0
        rr2 = (entry - tp2) / risk if risk else 0
        risk_tag = "low" if signal["score"] > 80 else "medium" if signal["score"] > 66 else "high"
        out = {
            "symbol": signal["symbol"],
            "setup": signal["setup"],
            "score": round(signal["score"], 2),
            "confidence": round(signal["confidence"], 2),
            "risk_tag": risk_tag,
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "rr1": rr1,
            "rr2": rr2,
            "ttl_expires_at": (datetime.now(timezone.utc) + timedelta(minutes=p.ttl_minutes)).isoformat(),
            "reasons": signal["reasons"],
            "invalidate_if": f"1m close above {sl:.6f} for 2 candles",
        }
        return out

    async def loop(self):
        while True:
            await self.scan_once()
            await asyncio.sleep(settings.scan_interval_sec)
