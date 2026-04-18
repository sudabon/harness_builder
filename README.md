# Harness Builder

コーディングエージェントのためのハーネスを生成する Web アプリケーションです。

## Stack

- Frontend: React + TypeScript + Vite + Tailwind CSS + shadcn-style UI
- Backend: FastAPI + SQLAlchemy + Alembic + Jinja2
- Database: PostgreSQL

## Local Development

### Docker Compose

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

### Backend Only

```bash
cd backend
uv sync --group dev
uv run pytest
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend Only

```bash
cd frontend
pnpm install
pnpm test
pnpm dev
```
