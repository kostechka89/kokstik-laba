# News API

FastAPI application implementing CRUD for users, news, and comments with JWT authentication, role checks, Redis caching, and Celery notifications.

## Features
- Users with roles (`user`, `admin`) and verification flag for authors.
- Password hashing with Argon2; JWT access/refresh tokens.
- Role enforcement: only verified authors or admins can create news; only authors/admins can edit/delete their content.
- Redis cache for news list and detail (TTL 5 minutes) and refresh sessions; in-memory fallback when Redis is unavailable.
- Celery tasks for new-news notifications and weekly digest (logged to `notifications.log`).

## Setup
1. Create virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Provide environment variables (or `.env`):
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/news
   SECRET_KEY=your-secret
   REDIS_URL=redis://localhost:6379/0
   GITHUB_CLIENT_ID=placeholder
   GITHUB_CLIENT_SECRET=placeholder
   ```
   SQLite is used by default if `DATABASE_URL` is not set.
3. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```
4. (Optional) Run Celery worker and beat for scheduled digest:
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   celery -A app.tasks.celery_app beat --loglevel=info
   ```

## Example requests
- Register user:
  ```bash
  curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"name":"Admin","email":"admin@example.com","password":"secret","role":"admin"}'
  ```
- Login:
  ```bash
  curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d 'username=admin@example.com&password=secret'
  ```
- Create news (requires verified author or admin, Authorization header with bearer token):
  ```bash
  curl -X POST http://localhost:8000/news/ -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
    -d '{"title":"Hello","content":{"body":"hi"},"author_id":1}'
  ```
- Create comment:
  ```bash
  curl -X POST http://localhost:8000/comments/ -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
    -d '{"text":"Nice","news_id":1,"author_id":1}'
  ```

## Testing
The codebase compiles under Python using:

```bash
python -m compileall app
```

## Notes
- Refresh sessions are stored in Redis (or in-memory fallback) with TTL derived from refresh token lifetime.
- News endpoints log when cache is used.
- Celery tasks log notification events to `notifications.log` to emulate email sending.
