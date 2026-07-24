from contextlib import asynccontextmanager
from datetime import UTC, datetime

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.application.services.auth_service import SeedService
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.schemas.common import HealthResponse, ResponseEnvelope

settings = get_settings()
setup_logging(settings.environment)
logger = structlog.get_logger()

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_app", app=settings.app_name, environment=settings.environment)
    async with AsyncSessionLocal() as session:
        seed_service = SeedService(session, settings)
        seeded = await seed_service.seed_if_empty()
        await session.commit()
        if seeded:
            logger.info("demo_seed_completed")
    yield
    logger.info("shutting_down_app")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"data": None, "errors": [exc.detail]})


@app.get("/health", response_model=ResponseEnvelope[HealthResponse], tags=["Health"])
async def health_check() -> ResponseEnvelope[HealthResponse]:
    return ResponseEnvelope(
        data=HealthResponse(
            status="healthy",
            version=settings.app_version,
            environment=settings.environment,
            timestamp=datetime.now(UTC),
        )
    )
