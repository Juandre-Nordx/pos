from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.infrastructure.database.models.user import CompanySettings, User
from app.schemas.common import ResponseEnvelope
from app.schemas.settings import CompanySettingsResponse, CompanySettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


async def _get_company_settings(session: AsyncSession) -> CompanySettings | None:
    result = await session.execute(
        select(CompanySettings)
        .where(CompanySettings.is_deleted.is_(False))
        .order_by(CompanySettings.id)
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/company", response_model=ResponseEnvelope[CompanySettingsResponse | None])
async def get_company_settings(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[CompanySettingsResponse | None]:
    settings = await _get_company_settings(session)
    return ResponseEnvelope(data=settings)


@router.put("/company", response_model=ResponseEnvelope[CompanySettingsResponse])
async def update_company_settings(
    payload: CompanySettingsUpdate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[CompanySettingsResponse]:
    settings = await _get_company_settings(session)
    values = payload.model_dump()
    values["address"] = payload.address.model_dump()

    if settings is None:
        settings = CompanySettings(**values, created_by=user.id, updated_by=user.id)
        session.add(settings)
    else:
        for field, value in values.items():
            setattr(settings, field, value)
        settings.updated_by = user.id

    await session.commit()
    await session.refresh(settings)
    return ResponseEnvelope(data=settings)
