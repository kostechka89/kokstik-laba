Fedotova A.

Полный проект из репозитория: https://github.com/itmo-webdev/WEBLABARATORNAYA_FEDOTOVA_A_A
 Он нужен для полноценной работы моего кода! Прошу прощения что все было загружено в отдельный репозиторий!!!!!

# Zadanie5

Коротко: подключены метрики Prometheus, графики Grafana, структурные JSON-логи и интеграция с Hawk для ошибок.

## Запуск через Docker Compose

```bash
docker compose up -d --build
```

## Примеры Invoke-RestMethod (PowerShell)

```powershell
$base = "http://localhost:8000"

Invoke-RestMethod -Method Get -Uri "$base/metrics"
Invoke-RestMethod -Method Get -Uri "$base/health"
Invoke-RestMethod -Method Get -Uri "$base/debug/boom"
```
