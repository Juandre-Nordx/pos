# NordxPOS

Production-ready ERP/POS platform for commercial deployment. Single-tenant per customer, optimized for South African businesses (ZAR, en-ZA).

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Vite, TailwindCSS, Shadcn UI |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL |
| Hosting | Railway |

## Quick Start (Local)

```bash
# Start PostgreSQL
docker compose -f docker/docker-compose.yml up -d postgres

# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
cp ..\.env.example ..\.env
alembic upgrade head
python -m scripts.seed_demo
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Demo login: `admin@demo.nordxpos.co.za` / `Demo@2026!`

## Project Structure

```
NordxPOS/
├── frontend/          React application
├── backend/           FastAPI application
├── database/          Seeds and reference SQL
├── docs/              Architecture and API docs
├── scripts/           Dev and deployment scripts
├── docker/            Docker Compose configs
└── .github/           CI/CD workflows
```

## Health Check

```
GET /health
```

## Railway deployment

The production frontend and backend run as separate Railway services. Configure
the frontend service with:

```text
VITE_API_URL=https://pos-production-62cf5.up.railway.app/api/v1
```

Configure the backend service to allow the frontend origin:

```text
CORS_ORIGINS=https://pos-frontend-production.up.railway.app,https://pos-forntend-production.up.railway.app
```

The second hostname preserves the spelling of the currently deployed Railway
frontend domain. A browser preflight (`OPTIONS /api/v1/auth/login`) returning
HTTP 400 means its exact origin is missing from `CORS_ORIGINS`; update the
backend variable and redeploy the backend before testing login again.

`VITE_API_URL` is embedded during the Vite build, so redeploy the frontend after
changing it. Never include `/auth/login` in this value; it must end at `/api/v1`.

After redeploying, a login request must appear in the **backend** service's
network logs as `POST /api/v1/auth/login` (not in the frontend service). Backend
deploy logs emit structured `login_attempt`, `login_success`, and `login_failed`
events. These events include the normalized email and original client IP but
never the submitted password or authorization token.

## License

Proprietary — NordxPOS. All rights reserved.
