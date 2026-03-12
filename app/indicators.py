from __future__ import annotations

import numpy as np


def safe_ret(cur: float, prev: float) -> float:
    if prev == 0:
        return 0.0
    return (cur - prev) / prev * 100


def rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    deltas = np.diff(np.array(closes, dtype=float))
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def ema(values: np.ndarray, span: int) -> np.ndarray:
    alpha = 2 / (span + 1)
    out = np.zeros_like(values)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def macd(closes: list[float]) -> dict:
    if len(closes) < 35:
        return {"line": 0.0, "signal": 0.0, "hist": 0.0, "hist_slope": 0.0}
    arr = np.array(closes, dtype=float)
    line = ema(arr, 12) - ema(arr, 26)
    signal = ema(line, 9)
    hist = line - signal
    return {
        "line": float(line[-1]),
        "signal": float(signal[-1]),
        "hist": float(hist[-1]),
        "hist_slope": float(hist[-1] - hist[-2]),
    }


def atr_pct(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 0.0
    highs_arr, lows_arr, closes_arr = np.array(highs), np.array(lows), np.array(closes)
    prev_close = np.roll(closes_arr, 1)
    prev_close[0] = closes_arr[0]
    tr = np.maximum(highs_arr - lows_arr, np.maximum(np.abs(highs_arr - prev_close), np.abs(lows_arr - prev_close)))
    atr = np.mean(tr[-period:])
    return float(atr / closes_arr[-1] * 100) if closes_arr[-1] else 0.0
