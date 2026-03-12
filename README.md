# MEXC Pump Reversal SHORT Dashboard

Профессиональный real-time dashboard для поиска шорт-сетапов после пампа на MEXC USDT-фьючерсах.

## Что реализовано
- Сканер ликвидных `_USDT` контрактов с фильтрами по цене/24h объёму.
- Детект сетапов: `pump_reversal_short`, `false_breakout_short`, `level_reject_short`, `knife_continuation_short`.
- Метрики: ret1/3/5/15, RSI(14), MACD histogram slope, VR, ATR%, spread/depth.
- Прозрачный скоринг (0–100), confidence, risk tag.
- Risk блок: entry/sl/tp1/tp2, RR, invalidate-if, TTL.
- Anti-spam: cooldown + dedup по symbol+setup + экстремум-фильтры.
- Telegram alerts (new signal).
- UI: Top Signals, Near Trigger watchlist, tracked journal, market regime panel.
- Presets: ULTRA-STRICT / BALANCED / FLOW.
- Хранение сигналов в SQLite.

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Откройте `http://localhost:8000`.

## Env-параметры
- `MEXC_BASE_URL` (default `https://contract.mexc.com`)
- `SCAN_INTERVAL_SEC`
- `MIN_24H_VOLUME_USDT`, `MAX_24H_VOLUME_USDT`
- `MAX_PRICE`, `PAIR_LIMIT`
- `COOLDOWN_MIN`, `VR_MAX_FILTER`, `RET15_MAX_FILTER`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

## Замечания
- Данные funding/OI/binance-divergence можно добавить отдельным модулем.
- Для backtest-модуля предусмотрена база сигналов + временные метрики в tracked журнале.
