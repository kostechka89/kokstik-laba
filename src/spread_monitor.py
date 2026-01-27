#!/usr/bin/env python3
import dataclasses
import json
import os
import time
from typing import Dict, Iterable, List, Optional, Tuple

import requests

GATE_API_BASE = "https://api.gateio.ws/api/v4"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"


@dataclasses.dataclass(frozen=True)
class GateTicker:
    currency_pair: str
    last: float


@dataclasses.dataclass(frozen=True)
class YahooQuote:
    symbol: str
    regular_market_price: Optional[float]
    premarket_price: Optional[float]
    currency: Optional[str]


@dataclasses.dataclass(frozen=True)
class SpreadAlert:
    gate_symbol: str
    gate_last: float
    yahoo_symbol: str
    yahoo_price: Optional[float]
    yahoo_premarket_price: Optional[float]
    spread_percent: Optional[float]


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return float(raw)


def _chunked(values: List[str], size: int) -> Iterable[List[str]]:
    for idx in range(0, len(values), size):
        yield values[idx: idx + size]


def load_symbol_mapping(path: str) -> Dict[str, str]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        if path.endswith(".json"):
            return json.load(handle)
        mapping = {}
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            gate_symbol, yahoo_symbol = [part.strip() for part in line.split(",", 1)]
            mapping[gate_symbol] = yahoo_symbol
        return mapping


def fetch_gate_tickers(quote_currency: str) -> List[GateTicker]:
    response = requests.get(f"{GATE_API_BASE}/spot/tickers", timeout=20)
    response.raise_for_status()
    tickers = []
    for item in response.json():
        pair = item.get("currency_pair")
        if not pair or not pair.endswith(f"_{quote_currency}"):
            continue
        try:
            last_value = float(item.get("last"))
        except (TypeError, ValueError):
            continue
        tickers.append(GateTicker(currency_pair=pair, last=last_value))
    return tickers


def fetch_yahoo_quotes(symbols: List[str]) -> Dict[str, YahooQuote]:
    quotes: Dict[str, YahooQuote] = {}
    for batch in _chunked(symbols, 200):
        params = {"symbols": ",".join(batch)}
        response = requests.get(YAHOO_QUOTE_URL, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        for item in payload.get("quoteResponse", {}).get("result", []):
            symbol = item.get("symbol")
            if not symbol:
                continue
            quotes[symbol] = YahooQuote(
                symbol=symbol,
                regular_market_price=item.get("regularMarketPrice"),
                premarket_price=item.get("preMarketPrice"),
                currency=item.get("currency"),
            )
    return quotes


def build_spread_alerts(
    gate_tickers: List[GateTicker],
    yahoo_quotes: Dict[str, YahooQuote],
    mapping: Dict[str, str],
    threshold: float,
) -> List[SpreadAlert]:
    alerts: List[SpreadAlert] = []
    for ticker in gate_tickers:
        gate_symbol = ticker.currency_pair
        yahoo_symbol = mapping.get(gate_symbol, gate_symbol.split("_")[0])
        quote = yahoo_quotes.get(yahoo_symbol)
        if quote is None:
            alerts.append(
                SpreadAlert(
                    gate_symbol=gate_symbol,
                    gate_last=ticker.last,
                    yahoo_symbol=yahoo_symbol,
                    yahoo_price=None,
                    yahoo_premarket_price=None,
                    spread_percent=None,
                )
            )
            continue
        yahoo_price = quote.regular_market_price
        premarket_price = quote.premarket_price
        comparison_price = yahoo_price
        if premarket_price is not None:
            comparison_price = premarket_price
        spread_percent = None
        if comparison_price is not None and comparison_price != 0:
            spread_percent = ((ticker.last - comparison_price) / comparison_price) * 100
        if spread_percent is None or abs(spread_percent) < threshold:
            continue
        alerts.append(
            SpreadAlert(
                gate_symbol=gate_symbol,
                gate_last=ticker.last,
                yahoo_symbol=yahoo_symbol,
                yahoo_price=yahoo_price,
                yahoo_premarket_price=premarket_price,
                spread_percent=spread_percent,
            )
        )
    return alerts


def format_alert(alert: SpreadAlert, threshold: float) -> str:
    spread_text = "N/A" if alert.spread_percent is None else f"{alert.spread_percent:.2f}%"
    return (
        f"SPREAD DETECTED >{threshold:.2f}%\n"
        f"📌 {alert.gate_symbol}\n\n"
        f"Last price (Gate): {alert.gate_last:.6f}\n"
        f"Yahoo Premarket Price: {alert.yahoo_premarket_price if alert.yahoo_premarket_price is not None else 'N/A'}\n"
        f"Yahoo Market Price: {alert.yahoo_price if alert.yahoo_price is not None else 'N/A'}\n"
        f"Spread vs Yahoo: {spread_text}\n"
        f"Yahoo symbol: {alert.yahoo_symbol}"
    )


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        data={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=20,
    )
    response.raise_for_status()


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    quote_currency = os.getenv("GATE_QUOTE_CURRENCY", "USDT")
    threshold = _get_env_float("SPREAD_THRESHOLD", 5.0)
    mapping_path = os.getenv("SYMBOL_MAPPING_PATH", "")
    poll_seconds = int(os.getenv("POLL_SECONDS", "60"))

    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    mapping = load_symbol_mapping(mapping_path)

    while True:
        gate_tickers = fetch_gate_tickers(quote_currency)
        yahoo_symbols = sorted({mapping.get(t.currency_pair, t.currency_pair.split("_")[0]) for t in gate_tickers})
        yahoo_quotes = fetch_yahoo_quotes(yahoo_symbols)
        alerts = build_spread_alerts(gate_tickers, yahoo_quotes, mapping, threshold)
        for alert in alerts:
            message = format_alert(alert, threshold)
            send_telegram_message(token, chat_id, message)
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
