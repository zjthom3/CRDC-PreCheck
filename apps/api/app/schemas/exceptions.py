from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from .common import IdentifiedModel


class ExceptionCreate(BaseModel):
    rule_result_id: UUID
    rationale: str | None = None
    due_date: date | None = None


class ExceptionUpdate(BaseModel):
    status: str | None = None
    owner_user_id: UUID | None = None
    rationale: str | None = None
    due_date: date | None = None
    approved: bool | None = None


class ExceptionRead(IdentifiedModel):
    district_id: UUID
    rule_result_id: UUID
    owner_user_id: UUID | None
    status: str
    rationale: str | None
    due_date: date | None
    approval_user_id: UUID | None
    approved_at: datetime | None


class ExceptionMemoCreate(BaseModel):
    title: str
    body_md: str
    generated_by: str = "user"


class ExceptionMemoRead(IdentifiedModel):
    district_id: UUID
    exception_id: UUID
    title: str
    body_md: str
    generated_by: str
