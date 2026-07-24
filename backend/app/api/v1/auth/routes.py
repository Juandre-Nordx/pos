from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import AuthService
from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.infrastructure.database.models.user import User
from app.schemas.common import LoginRequest, ResponseEnvelope, TokenResponse, UserResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=ResponseEnvelope[TokenResponse])
async def login(
    payload: LoginRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ResponseEnvelope[TokenResponse]:
    service = AuthService(session, settings)
    user, access_token, refresh_token = await service.login(
        payload.email,
        payload.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    logger.info("login_success", user_uuid=str(user.uuid))
    return ResponseEnvelope(
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token)
    )


@router.get("/me", response_model=ResponseEnvelope[UserResponse])
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ResponseEnvelope[UserResponse]:
    service = AuthService(session, settings)
    user = await service.get_current_user_profile(current_user)
    return ResponseEnvelope(
        data=UserResponse(
            uuid=user.uuid,
            created_at=user.created_at,
            updated_at=user.updated_at,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            roles=[role.slug for role in user.roles],
        )
    )
