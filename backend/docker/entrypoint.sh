#!/bin/sh
set -e

echo "Starting backend..."

# If DATABASE_URL points to postgres in compose, wait a bit for readiness
if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL is set. Waiting for database..."
  # naive wait loop (no extra tools)
  for i in $(seq 1 60); do
    python -c "import os,sys; import sqlalchemy as sa; 
url=os.environ.get('DATABASE_URL'); 
try:
  e=sa.create_engine(url); 
  with e.connect() as c: c.execute(sa.text('SELECT 1')); 
  print('DB OK'); 
  sys.exit(0)
except Exception as ex:
  sys.exit(1)
" && break || true
    sleep 1
  done
fi

echo "Running migrations..."
alembic upgrade head || true

echo "Launching Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
