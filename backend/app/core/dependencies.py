from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.infrastructure.database.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if credentials is None:
        raise UnauthorizedException()

    try:
        payload = decode_token(credentials.credentials, settings)
    except ValueError as exc:
        raise UnauthorizedException("Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    user_uuid = payload.get("sub")
    if not user_uuid:
        raise UnauthorizedException("Invalid token subject")

    result = await session.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.uuid == user_uuid, User.is_deleted.is_(False), User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedException("User not found or inactive")
    return user


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, session, settings)
    except UnauthorizedException:
        return None


def require_permission(permission: str):
    async def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not user.has_permission(permission):
            raise ForbiddenException(f"Missing permission: {permission}")
        return user

    return checker


async def get_request_id(
    x_request_id: Annotated[str | None, Header()] = None,
) -> str:
    return x_request_id or "unknown"
