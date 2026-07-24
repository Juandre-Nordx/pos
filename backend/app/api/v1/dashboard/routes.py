from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.dashboard_service import DashboardService
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.infrastructure.database.models.user import User
from app.schemas.common import ResponseEnvelope
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=ResponseEnvelope[DashboardResponse])
async def get_dashboard(
    _: Annotated[User, Depends(require_permission("dashboard:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[DashboardResponse]:
    service = DashboardService(session)
    data = await service.get_dashboard()
    return ResponseEnvelope(data=data)
