from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from department_ai.core.config.settings import Settings, get_settings
from department_ai.infrastructure.database.session import get_db_session
from department_ai.modules.identity.infrastructure.models import (
    OrganizationMembership,
    User,
)
from department_ai.modules.identity.infrastructure.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: DatabaseSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token, settings)
    except InvalidTokenError:
        raise credentials_error from None

    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_organization_admin(
    organization_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> None:
    membership = session.get(
        OrganizationMembership,
        (current_user.id, organization_id),
    )
    if membership is None or membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization administrator role required",
        )
