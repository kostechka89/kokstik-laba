# MEXC Pump Reversal SHORT Dashboard

Профессиональный real-time дэшборд для поиска SHORT-сетапов после пампа на MEXC USDT-фьючерсах.

## Что умеет система
- Сканирует ликвидные `_USDT` контракты по фильтрам цены и 24h-объёма.
- Детектирует сетапы:
  - `pump_reversal_short`
  - `false_breakout_short`
  - `level_reject_short`
  - `knife_continuation_short` (агрессивный вариант)
- Считает метрики: `ret1/ret3/ret5/ret15`, `RSI(14)`, `MACD`, `VR`, `ATR%`, `spread/depth`.
- Выдает actionable-сигнал: `entry/sl/tp1/tp2`, `confidence`, `score`, `risk_tag`, `invalidate_if`, `ttl`.
- Ведет журнал сигналов в SQLite + отдает top/near/tracked для UI.
- Поддерживает Telegram-алерты.
- Поддерживает пресеты: `ULTRA-STRICT`, `BALANCED`, `FLOW`.

---

## Быстрый старт через Docker (рекомендуется)

### 1) Подготовка
```bash
cp .env.example .env
mkdir -p data
```

### 2) Запуск
```bash
docker compose up --build -d
```

### 3) Проверка
- UI: `http://localhost:8000/`
- JSON API: `http://localhost:8000/api/dashboard`
- Swagger/OpenAPI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4) Логи
```bash
docker compose logs -f mexc-short-dashboard
```

### 5) Остановка
```bash
docker compose down
```

> База сигналов сохраняется в `./data/signals.db` (volume mount в контейнер `/app/data`).

---

## Запуск без Docker
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Открыть: `http://localhost:8000/`

---

## API: URL и контракт

Базовый URL локально:
- `http://localhost:8000`

### `GET /`
Возвращает HTML-дэшборд.

### `GET /api/dashboard`
Возвращает агрегированные данные для UI:
- `top_signals`: top активных сигналов (до 10)
- `watchlist_near_trigger`: пары near-trigger
- `tracked`: последние сигналы из журнала
- `regime`: режим рынка (`RISK-ON` / `MIXED` / `RISK-OFF`), число активных пампов, средняя волатильность

Пример:
```bash
curl -s http://localhost:8000/api/dashboard | jq
```

### `POST /api/preset`
Переключение пресета сканера.

Body:
```json
{
  "preset": "BALANCED"
}
```

Доступные значения:
- `ULTRA-STRICT`
- `BALANCED`
- `FLOW`

Пример:
```bash
curl -X POST http://localhost:8000/api/preset \
  -H 'content-type: application/json' \
  -d '{"preset":"ULTRA-STRICT"}'
```

### `GET /docs`
Автогенерируемая документация FastAPI (Swagger UI).

---

## Внешние API источники (MEXC)
Используются публичные market endpoints:
- `GET /api/v1/contract/detail` — список контрактов
- `GET /api/v1/contract/ticker` — 24h тикеры
- `GET /api/v1/contract/kline/{symbol}` — свечи (Min1/Min5/Min15)
- `GET /api/v1/contract/depth/{symbol}` — стакан L2

Базовый URL по умолчанию:
- `https://contract.mexc.com`

Настраивается через `MEXC_BASE_URL` в `.env`.

---

## Конфигурация `.env`
Ключевые параметры:
- `MEXC_BASE_URL`
- `SCAN_INTERVAL_SEC`
- `MIN_24H_VOLUME_USDT`, `MAX_24H_VOLUME_USDT`
- `MAX_PRICE`, `PAIR_LIMIT`
- `COOLDOWN_MIN`, `VR_MAX_FILTER`, `RET15_MAX_FILTER`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `DB_PATH` (например `/app/data/signals.db` в Docker)

См. шаблон: `.env.example`.

---

## Telegram алерты
Для включения укажите в `.env`:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Событие: `new signal`.

Сообщение содержит:
- symbol
- setup
- entry/sl/tp1/tp2
- confidence + score
- причины сигнала (`ret/RSI/VR/level`)

---

## Ограничения текущей версии
- Funding / Open Interest / Binance cross-check пока не подключены (можно добавить отдельным модулем).
- Бэктест-оценка хранится как основа в журнале сигналов, без отдельного отчётного движка first-touch статистики.
