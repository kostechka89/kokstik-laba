Fedotova A.

Полный проект из репозитория: https://github.com/itmo-webdev/WEBLABARATORNAYA_FEDOTOVA_A_A
 Он нужен для полноценной работы моего кода! Прошу прощения что все было загружено в отдельный репозиторий!!!!!

# Zadanie2

Коротко: добавлена авторизация, роли, GitHub OAuth, JWT/refresh и ограничения на редактирование своих новостей и комментариев.

## Запуск через Docker Compose

```bash
docker compose up -d --build
```

## Примеры Invoke-RestMethod (PowerShell)

```powershell
$base = "http://localhost:8000"

Invoke-RestMethod -Method Post -Uri "$base/auth/register" -ContentType "application/json" -Body (ConvertTo-Json @{ name = "Author"; email = "author2@example.com"; password = "Pass123!"; is_verified_author = $true; is_admin = $false; avatar = $null })
Invoke-RestMethod -Method Post -Uri "$base/auth/register" -ContentType "application/json" -Body (ConvertTo-Json @{ name = "Reader"; email = "reader2@example.com"; password = "Pass123!"; is_verified_author = $false; is_admin = $false; avatar = $null })

$authorTokens = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" -Body (ConvertTo-Json @{ email = "author2@example.com"; password = "Pass123!" })
$authorHeaders = @{ Authorization = "Bearer $($authorTokens.access_token)" }

$news = Invoke-RestMethod -Method Post -Uri "$base/news" -Headers $authorHeaders -ContentType "application/json" -Body (ConvertTo-Json @{ title = "Новость"; content = @{ text = "Текст" }; cover = $null })

$readerTokens = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" -Body (ConvertTo-Json @{ email = "reader2@example.com"; password = "Pass123!" })
$readerHeaders = @{ Authorization = "Bearer $($readerTokens.access_token)" }

$comment = Invoke-RestMethod -Method Post -Uri "$base/comments" -Headers $readerHeaders -ContentType "application/json" -Body (ConvertTo-Json @{ text = "Ок"; news_id = $news.id })

Invoke-RestMethod -Method Get -Uri "$base/auth/sessions" -Headers $authorHeaders
Invoke-RestMethod -Method Post -Uri "$base/auth/refresh" -ContentType "application/json" -Body (ConvertTo-Json @{ refresh_token = $authorTokens.refresh_token })
Invoke-RestMethod -Method Post -Uri "$base/auth/logout" -ContentType "application/json" -Body (ConvertTo-Json @{ refresh_token = $authorTokens.refresh_token })
```
