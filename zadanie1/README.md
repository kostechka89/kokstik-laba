Fedotova A.

Полный проект из репозитория: https://github.com/itmo-webdev/WEBLABARATORNAYA_FEDOTOVA_A_A
 Он нужен для полноценной работы моего кода! Прошу прощения что все было загружено в отдельный репозиторий!!!!!

# Zadanie1

Коротко: базовый CRUD по пользователям, новостям и комментариям, миграции и связи между сущностями.

## Запуск через Docker Compose

```bash
docker compose up -d --build
```

## Примеры Invoke-RestMethod (PowerShell)

```powershell
$base = "http://localhost:8000"

Invoke-RestMethod -Method Post -Uri "$base/auth/register" -ContentType "application/json" -Body (ConvertTo-Json @{ name = "Author"; email = "author1@example.com"; password = "Pass123!"; is_verified_author = $true; is_admin = $false; avatar = $null })
Invoke-RestMethod -Method Post -Uri "$base/auth/register" -ContentType "application/json" -Body (ConvertTo-Json @{ name = "Reader"; email = "reader1@example.com"; password = "Pass123!"; is_verified_author = $false; is_admin = $false; avatar = $null })

$authorTokens = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" -Body (ConvertTo-Json @{ email = "author1@example.com"; password = "Pass123!" })
$authorHeaders = @{ Authorization = "Bearer $($authorTokens.access_token)" }

$news = Invoke-RestMethod -Method Post -Uri "$base/news" -Headers $authorHeaders -ContentType "application/json" -Body (ConvertTo-Json @{ title = "Первая новость"; content = @{ text = "Текст" }; cover = $null })

$readerTokens = Invoke-RestMethod -Method Post -Uri "$base/auth/login" -ContentType "application/json" -Body (ConvertTo-Json @{ email = "reader1@example.com"; password = "Pass123!" })
$readerHeaders = @{ Authorization = "Bearer $($readerTokens.access_token)" }

$comment = Invoke-RestMethod -Method Post -Uri "$base/comments" -Headers $readerHeaders -ContentType "application/json" -Body (ConvertTo-Json @{ text = "Отлично"; news_id = $news.id })

Invoke-RestMethod -Method Patch -Uri "$base/news/$($news.id)" -Headers $authorHeaders -ContentType "application/json" -Body (ConvertTo-Json @{ title = "Обновленная новость" })
Invoke-RestMethod -Method Patch -Uri "$base/comments/$($comment.id)" -Headers $readerHeaders -ContentType "application/json" -Body (ConvertTo-Json @{ text = "Очень хорошо" })

Invoke-RestMethod -Method Delete -Uri "$base/news/$($news.id)" -Headers $authorHeaders
```
