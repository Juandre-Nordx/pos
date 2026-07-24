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

## License

Proprietary — NordxPOS. All rights reserved.
