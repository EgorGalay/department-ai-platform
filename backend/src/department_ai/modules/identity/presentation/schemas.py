from typing import Literal
from uuid import UUID

from pydantic import BaseModel

type OrganizationRole = Literal["admin", "teacher", "student"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class MembershipResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    role: OrganizationRole


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    memberships: list[MembershipResponse]


class OrganizationMemberResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    role: OrganizationRole
