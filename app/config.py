from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict
import os


@dataclass(frozen=True)
class Preset:
    name: str
    ret5_min: float
    ret15_min: float
    rsi_min: float
    rsi_max: float
    vr_min: float
    score_min: float
    ttl_minutes: int


PRESETS: Dict[str, Preset] = {
    "ULTRA-STRICT": Preset("ULTRA-STRICT", ret5_min=2.8, ret15_min=5.0, rsi_min=66, rsi_max=84, vr_min=1.9, score_min=74, ttl_minutes=10),
    "BALANCED": Preset("BALANCED", ret5_min=2.2, ret15_min=4.2, rsi_min=62, rsi_max=86, vr_min=1.6, score_min=66, ttl_minutes=12),
    "FLOW": Preset("FLOW", ret5_min=1.6, ret15_min=3.2, rsi_min=58, rsi_max=88, vr_min=1.3, score_min=56, ttl_minutes=15),
}


@dataclass
class Settings:
    mexc_base_url: str = field(default_factory=lambda: os.getenv("MEXC_BASE_URL", "https://contract.mexc.com"))
    scan_interval_sec: int = field(default_factory=lambda: int(os.getenv("SCAN_INTERVAL_SEC", "20")))
    min_24h_volume_usdt: float = field(default_factory=lambda: float(os.getenv("MIN_24H_VOLUME_USDT", "3000000")))
    max_24h_volume_usdt: float = field(default_factory=lambda: float(os.getenv("MAX_24H_VOLUME_USDT", "10000000000")))
    max_price: float = field(default_factory=lambda: float(os.getenv("MAX_PRICE", "250")))
    pair_limit: int = field(default_factory=lambda: int(os.getenv("PAIR_LIMIT", "80")))
    cooldown_minutes: int = field(default_factory=lambda: int(os.getenv("COOLDOWN_MIN", "12")))
    vr_max_filter: float = field(default_factory=lambda: float(os.getenv("VR_MAX_FILTER", "5.8")))
    ret15_max_filter: float = field(default_factory=lambda: float(os.getenv("RET15_MAX_FILTER", "15.0")))
    telegram_token: str | None = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN"))
    telegram_chat_id: str | None = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID"))


settings = Settings()
