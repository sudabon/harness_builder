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

Alembic is the canonical schema history. When changing SQLAlchemy models, update
the matching Alembic revision in the same change and verify the migration path.

Common local checks:

```bash
uv run alembic history
uv run alembic heads
uv run alembic current
uv run alembic upgrade head
```

To test against a throwaway SQLite database:

```bash
DATABASE_URL=sqlite:///./tmp-migration-check.db uv run alembic upgrade head
DATABASE_URL=sqlite:///./tmp-migration-check.db uv run alembic current
```
