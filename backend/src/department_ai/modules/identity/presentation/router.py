from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from department_ai.core.config.settings import Settings, get_settings
from department_ai.modules.identity.infrastructure.models import (
    Organization,
    OrganizationMembership,
    User,
)
from department_ai.modules.identity.infrastructure.security import (
    create_access_token,
    verify_password,
)
from department_ai.modules.identity.presentation.dependencies import (
    CurrentUser,
    DatabaseSession,
    require_organization_admin,
)
from department_ai.modules.identity.presentation.schemas import (
    MembershipResponse,
    OrganizationMemberResponse,
    OrganizationRole,
    TokenResponse,
    UserProfileResponse,
)

router = APIRouter(tags=["identity"])


@router.post("/auth/token", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DatabaseSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    if len(form_data.password) > 1024:
        raise _invalid_credentials()

    email = form_data.username.strip().casefold()
    user = session.scalar(select(User).where(User.email == email))
    password_is_valid = verify_password(
        form_data.password,
        user.password_hash if user is not None else None,
    )
    if user is None or not user.is_active or not password_is_valid:
        raise _invalid_credentials()

    return TokenResponse(access_token=create_access_token(user.id, settings))


@router.get("/auth/me", response_model=UserProfileResponse)
def get_profile(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> UserProfileResponse:
    memberships = session.execute(
        select(OrganizationMembership, Organization)
        .join(Organization, Organization.id == OrganizationMembership.organization_id)
        .where(OrganizationMembership.user_id == current_user.id)
        .order_by(Organization.name)
    ).all()

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        memberships=[
            MembershipResponse(
                organization_id=membership.organization_id,
                organization_name=organization.name,
                role=cast(OrganizationRole, membership.role),
            )
            for membership, organization in memberships
        ],
    )


@router.get(
    "/organizations/{organization_id}/members",
    response_model=list[OrganizationMemberResponse],
    dependencies=[Depends(require_organization_admin)],
)
def list_organization_members(
    organization_id: UUID,
    session: DatabaseSession,
) -> list[OrganizationMemberResponse]:
    members = session.execute(
        select(User, OrganizationMembership.role)
        .join(OrganizationMembership, OrganizationMembership.user_id == User.id)
        .where(OrganizationMembership.organization_id == organization_id)
        .order_by(User.full_name)
    ).all()

    return [
        OrganizationMemberResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=cast(OrganizationRole, role),
        )
        for user, role in members
    ]


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
