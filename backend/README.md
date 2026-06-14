# Harness Builder Backend

FastAPI backend for the Harness Builder MVP.

`POST /api/v1/projects/{id}/generate` stores an OpenSpec change package in
`generated_files` instead of flat harness files. The package paths are rooted at
`openspec/changes/setup-ai-harness/` and include `proposal.md`, `tasks.md`,
`.openspec.yaml`, and `specs/ai-coding-harness/spec.md`. The original harness
templates are rendered as reference drafts inside `tasks.md`.

`GET /api/v1/projects/{id}/export` zips the saved `file_path` values as-is, so
extracting the ZIP at a target repository root places the change under
`openspec/changes/`. Run `/opsx:apply setup-ai-harness` in that repository to
create the final harness files.

## Development

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload --port 8000
```

## Database

The backend uses PostgreSQL in `docker-compose.yml`. API tests override the database
dependency with in-memory SQLite, but app startup still opens `DATABASE_URL` to
initialize schema metadata.

`task test` sets `DATABASE_URL` to the local `laborman` database by default.
`tests/conftest.py` applies the same default when the variable is unset.

```bash
task test
```

To use a different database for tests:

```bash
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname task test
```

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
