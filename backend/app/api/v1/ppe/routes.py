from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.ppe_service import PPEService
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.infrastructure.database.models.user import User
from app.schemas.common import ResponseEnvelope
from app.schemas.ppe import PPECategoryResponse, PPEComplianceSummary, PPEIssueResponse, PPEItemResponse

router = APIRouter(prefix="/ppe", tags=["PPE"])


@router.get("/categories", response_model=ResponseEnvelope[list[PPECategoryResponse]])
async def list_categories(
    _: Annotated[User, Depends(require_permission("ppe:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[list[PPECategoryResponse]]:
    service = PPEService(session)
    return ResponseEnvelope(data=await service.list_categories())


@router.get("/items", response_model=ResponseEnvelope[list[PPEItemResponse]])
async def list_items(
    _: Annotated[User, Depends(require_permission("ppe:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[list[PPEItemResponse]]:
    service = PPEService(session)
    return ResponseEnvelope(data=await service.list_items())


@router.get("/issues", response_model=ResponseEnvelope[list[PPEIssueResponse]])
async def list_issues(
    _: Annotated[User, Depends(require_permission("ppe:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[list[PPEIssueResponse]]:
    service = PPEService(session)
    return ResponseEnvelope(data=await service.list_issues())


@router.get("/compliance", response_model=ResponseEnvelope[PPEComplianceSummary])
async def compliance_summary(
    _: Annotated[User, Depends(require_permission("ppe:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[PPEComplianceSummary]:
    service = PPEService(session)
    return ResponseEnvelope(data=await service.compliance_summary())
