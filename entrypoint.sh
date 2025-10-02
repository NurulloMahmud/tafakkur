#!/bin/sh
set -e

# Wait for Postgres (host machine)
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  until nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.5
  done
  echo "Postgres is up."
fi

# Hardcoded Elasticsearch URL (docker-compose service)
ES_URL="http://es:9200"
echo "Waiting for Elasticsearch at $ES_URL..."
until curl -sf "$ES_URL" >/dev/null; do
  sleep 0.5
done
echo "Elasticsearch is ready."

python manage.py migrate --noinput

# Bootstrap ES indices and index current DB data
python manage.py es_boot_strap || true

if [ "$COLLECT_STATIC" = "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"