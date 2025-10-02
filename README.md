# Tafakkur DRF + Elasticsearch

## Overview

Django REST Framework project with two apps (`users`, `products`). Product search is powered by Elasticsearch via `elasticsearch-dsl`. The project runs with Docker Compose for a one-command local setup.

This README contains everything needed to run the project end-to-end.

## Prerequisites

- Docker and Docker Compose installed
- A PostgreSQL database (by default, using your host's Postgres). Optional snippet to run Postgres in Docker is provided.
- `curl` (optional) for quick health checks

## Quick Start

1. **Create `.env` from example:**
   ```bash
   cp .env.example .env
   ```

2. **Start services:**
   ```bash
   docker compose up --build
   ```

3. **Access:**
   - API: http://localhost:8000
   - Elasticsearch (sanity): http://localhost:9200

4. **Test product search:**
   ```
   GET http://localhost:8000/products/products/search/?q=lap
   ```

On startup, the app waits for Postgres and Elasticsearch, runs migrations, bootstraps Elasticsearch indices, indexes existing data (if any), and starts Gunicorn.

## Project Structure (key files/folders)

```
.
├── manage.py
├── conf/
│   ├── settings.py
│   └── wsgi.py
├── products/
│   ├── models.py
│   ├── views.py
│   ├── documents.py
│   └── management/
│       └── commands/
│           └── es_bootstrap.py
├── users/
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Setup

Create and edit `.env` (copy from `.env.example`). For macOS/Windows with Docker Desktop use `host.docker.internal` as `DB_HOST`. For Linux, `host.docker.internal` works if `host-gateway` is enabled (already configured), otherwise use your host IP.

### Example `.env` (copy this verbatim if unsure):

```env
DJANGO_SETTINGS_MODULE=conf.settings
SECRET_KEY=dev-secret
DEBUG=1
ALLOWED_HOSTS=*

# Host Postgres (default). If you run Postgres in Docker, set DB_HOST=db
DB_NAME=tafakkur
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=host.docker.internal
DB_PORT=5432

# Static files (0/1)
COLLECT_STATIC=0
```

**Note:**
- Elasticsearch is hardcoded in `settings.py` to `http://es:9200` for simplicity. No ES env vars are needed.

## Docker Services

- **web**: Django (Gunicorn). Waits for DB/ES, runs migrations and `es_bootstrap`, then starts the app.
- **es**: Elasticsearch 8.x single-node (no auth).

### Published ports:
- `web` → 8000
- `es` → 9200

## Run, Stop, Rebuild

### Run:
```bash
docker compose up --build
```

### Stop:
```bash
docker compose down
```

### Rebuild cleanly (after dependency or entrypoint changes):
```bash
docker compose build --no-cache web
docker compose up
```

## Optional: Postgres in Docker

If you don't have Postgres locally, add this under `services:` in `docker-compose.yml`:

```yaml
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tafakkur
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d tafakkur"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - pg_data:/var/lib/postgresql/data
```

Then set in `.env`:
```env
DB_HOST=db
```

Also ensure `volumes` section includes:
```yaml
volumes:
  es_data:
  pg_data:
```

## Useful Commands

### Apply migrations:
```bash
docker compose exec web python manage.py migrate
```

### Create superuser:
```bash
docker compose exec web python manage.py createsuperuser
```

### Bootstrap Elasticsearch (create indices and index existing DB rows):
```bash
docker compose exec web python manage.py es_bootstrap
```

### Django shell:
```bash
docker compose exec web python manage.py shell
```

### Run tests:
```bash
docker compose exec web pytest
```

### Exec into the container:
```bash
docker compose exec web sh
```

## API Endpoints (examples)

**Base URL:** http://localhost:8000

### Product search:
```
GET /products/products/search/?q=lap
```
Returns paginated products matched by Elasticsearch (e.g., title, description fields).

### Category search (if implemented similarly):
```
GET /products/categories/search/?q=laptop
```

Authentication and other endpoints depend on your `users` app and DRF configuration.

## Elasticsearch Notes

- `settings.py` hardcodes ES to the docker-compose service:
  ```python
  ELASTICSEARCH_DSL = { 'default': { 'hosts': ['http://es:9200'] } }
  ```
- Indices are defined in `products/documents.py` (e.g., "products", "categories").
- On startup, `entrypoint.sh` runs:
  ```bash
  python manage.py es_bootstrap
  ```
  This creates indices if missing and indexes existing Product/Category rows.

### If you see `index_not_found_exception`:
```bash
docker compose exec web python manage.py es_bootstrap
```

## Troubleshooting

### Postgres connection refused:
- Ensure `DB_HOST` is correct:
  - macOS/Windows host DB: `host.docker.internal`
  - Linux: `host.docker.internal` (with `host-gateway`) or your host IP
- Confirm Postgres is running and listening on `DB_PORT` (default 5432).

### Elasticsearch not reachable:
- We hardcode `http://es:9200`; check:
  ```bash
  docker compose logs es
  curl http://localhost:9200  # should return cluster JSON
  ```

### `ModuleNotFoundError: No module named 'conf'`:
- Ensure `conf/` exists at repo root next to `manage.py`
- Compose mounts `.:/app`; verify `/app/conf` exists inside the container
- Gunicorn command targets `conf.wsgi:application`

### `entrypoint.sh` "exec format error":
- Ensure LF line endings and executable bit:
  ```bash
  chmod +x entrypoint.sh
  ```
- Rebuild:
  ```bash
  docker compose build --no-cache web
  ```

### Empty search results:
- Ensure there are Products in the DB
- Run `es_boot_strap` to index existing rows
- Re-save a product to trigger indexing signals (if configured)

## Development Tips

- **Live reload**: code is bind-mounted into the container; save and refresh.
- **Seed data**: use Django admin or shell to create Products/Categories, then run `es_bootstrap` to index them.
- **Adjust search behavior** in `products/documents.py` (mappings/analyzers) and `products/views.py` (queries).

## Production Notes

This setup is for local/dev. For production:

- Use env vars for ES/DB, persistent volumes, managed services.
- Add reverse proxy (nginx) and HTTPS.
- Harden settings and logging.

## `.env.example` (create this file at repo root)

```env
DJANGO_SETTINGS_MODULE=conf.settings
SECRET_KEY=dev-secret
DEBUG=1
ALLOWED_HOSTS=*

# Host Postgres (default). For Dockerized Postgres, set DB_HOST=db
DB_NAME=tafakkur
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=host.docker.internal
DB_PORT=5432
```
