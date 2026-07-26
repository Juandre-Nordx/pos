FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend into the image
COPY backend/ ./

# Install the application and its dependencies
RUN pip install --no-cache-dir .

RUN mkdir -p /data/uploads

EXPOSE 8000

CMD sh -c 'alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"'