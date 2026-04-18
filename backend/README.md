# Harness Builder Backend

FastAPI backend for the Harness Builder MVP.

## Development

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload --port 8000
```

## Database

The backend uses PostgreSQL in `docker-compose.yml`. Tests override the database
dependency with SQLite so they can run locally without a container.
