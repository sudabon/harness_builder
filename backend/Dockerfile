FROM python:3.13-slim-trixie

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends cron vim && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

    # Copy project & library files
COPY pyproject.toml requirements.lock ./

# Install dependencies
RUN PYTHONDONTWRITEBYTECODE=1 pip install --break-system-packages --no-cache-dir -r requirements.lock

# Copy source code
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
COPY app /app/app
COPY public /app/public
COPY .env.pro /app/.env

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
