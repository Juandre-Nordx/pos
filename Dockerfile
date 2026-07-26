FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only the Python project first for better layer caching
COPY backend/pyproject.toml ./

# Install your application and dependencies
RUN pip install --no-cache-dir .

# Copy the rest of the backend source
COPY backend/ ./

RUN mkdir -p /data/uploads

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]CMD sh -c 'alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"'