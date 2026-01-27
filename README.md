# Gate ↔ Yahoo spread monitor

Этот скрипт парсит все пары на Gate.io с выбранной котируемой валютой (по умолчанию `USDT`), сопоставляет базовый тикер с Yahoo Finance и отправляет алерты в Telegram, когда спред между ценой на Gate и Yahoo превышает порог.

## Возможности

- Сравнение **Last price на Gate.io** с **Yahoo Market / Premarket**.
- Пакетные запросы к Yahoo Finance.
- Опциональная таблица маппинга тикеров для нестандартных названий.

## Быстрый старт

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Экспортируйте переменные окружения:

```bash
export TELEGRAM_BOT_TOKEN="<token>"
export TELEGRAM_CHAT_ID="@your_channel_or_chat_id"
export SPREAD_THRESHOLD="5"
```

3. Запустите монитор:

```bash
python src/spread_monitor.py
```

## Переменные окружения

| Переменная | По умолчанию | Описание |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | — | токен Telegram бота (обязательно) |
| `TELEGRAM_CHAT_ID` | — | ID чата или `@channel` (обязательно) |
| `SPREAD_THRESHOLD` | `5` | порог в процентах |
| `GATE_QUOTE_CURRENCY` | `USDT` | котируемая валюта для пар Gate.io |
| `POLL_SECONDS` | `60` | интервал опроса |
| `SYMBOL_MAPPING_PATH` | — | путь к `json` или `csv` маппингу тикеров |

## Маппинг тикеров

По умолчанию используется базовый тикер из пары Gate (например, `BTGO` из `BTGO_USDT`). Если Yahoo использует другой тикер, создайте файл:

**JSON**

```json
{
  "BTGO_USDT": "BTGO",
  "BRK_B_USDT": "BRK-B"
}
```

**CSV**

```text
BTGO_USDT,BTGO
BRK_B_USDT,BRK-B
```

И задайте:

```bash
export SYMBOL_MAPPING_PATH="/path/to/mapping.json"
```

## Пример сообщения

```
SPREAD DETECTED >5.00%
📌 BTGO_USDT

Last price (Gate): 12.340000
Yahoo Premarket Price: 12.1000
Yahoo Market Price: 12.2000
Spread vs Yahoo: 1.98%
Yahoo symbol: BTGO
```
