from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from .common import IdentifiedModel


class SSOLoginRequest(BaseModel):
    provider: str
    subject: str
    email: EmailStr
    display_name: str


class UserRead(IdentifiedModel):
    district_id: UUID
    email: EmailStr
    display_name: str
    role: str
    is_active: bool
    sso_provider: str | None
    sso_subject: str | None
    last_login_at: datetime | None


class AuthResponse(BaseModel):
    token: str
    user: UserRead
