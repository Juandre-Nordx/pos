FROM node:22-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build


FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend into the image
COPY backend/ ./

# Serve the compiled frontend from the same origin as the API. This keeps
# browser requests to /api/v1 away from a static frontend host, which rejects
# POST requests such as login with HTTP 405.
COPY --from=frontend-build /frontend/dist ./static

# Install the application and its dependencies
RUN pip install --no-cache-dir .

RUN mkdir -p /data/uploads

EXPOSE 8000

CMD sh -c 'alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"'
