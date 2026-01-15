Fedotova A.

Полный проект из репозитория: https://github.com/itmo-webdev/WEBLABARATORNAYA_FEDOTOVA_A_A
 Он нужен для полноценной работы моего кода! Прошу прощения что все было загружено в отдельный репозиторий!!!!!

# Zadanie4

Коротко: добавлены фоновые уведомления о новостях и еженедельный дайджест через Celery, с логированием в файл.

## Запуск через Docker Compose

```bash
docker compose up -d --build
```

## Примеры Invoke-RestMethod (PowerShell)

```powershell
$base = "http://localhost:8000"

Invoke-RestMethod -Method Post -Uri "$base/auth/register" -ContentType "application/json" -Body (ConvertTo-Json @{ name = "Author"; email = "author4@example.com"; password = "Pass123!"; is_verified_author = $true; is_admin = $false; avatar = $null })

$tokens = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" -Body (ConvertTo-Json @{ email = "author4@example.com"; password = "Pass123!" })
$headers = @{ Authorization = "Bearer $($tokens.access_token)" }

Invoke-RestMethod -Method Post -Uri "$base/news" -Headers $headers -ContentType "application/json" -Body (ConvertTo-Json @{ title = "С уведомлением"; content = @{ text = "Текст" }; cover = $null })
```
