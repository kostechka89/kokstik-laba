Fedotova A.

Полный проект из репозитория: https://github.com/itmo-webdev/WEBLABARATORNAYA_FEDOTOVA_A_A
 Он нужен для полноценной работы моего кода! Прошу прощения что все было загружено в отдельный репозиторий!!!!!

# Zadanie3

Коротко: добавлен Redis-кэш для новостей и пользовательских сессий, а также ускорение авторизации через кэш.

## Запуск через Docker Compose

```bash
docker compose up -d --build
```

## Примеры Invoke-RestMethod (PowerShell)

```powershell
$base = "http://localhost:8000"

Invoke-RestMethod -Method Post -Uri "$base/auth/register" -ContentType "application/json" -Body (ConvertTo-Json @{ name = "Author"; email = "author3@example.com"; password = "Pass123!"; is_verified_author = $true; is_admin = $false; avatar = $null })

$tokens = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" -Body (ConvertTo-Json @{ email = "author3@example.com"; password = "Pass123!" })
$headers = @{ Authorization = "Bearer $($tokens.access_token)" }

$news = Invoke-RestMethod -Method Post -Uri "$base/news" -Headers $headers -ContentType "application/json" -Body (ConvertTo-Json @{ title = "Кэш"; content = @{ text = "Текст" }; cover = $null })

Invoke-RestMethod -Method Get -Uri "$base/news/$($news.id)"
Invoke-RestMethod -Method Get -Uri "$base/news/$($news.id)"
```
