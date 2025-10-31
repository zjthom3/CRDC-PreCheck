from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .common import IdentifiedModel


class RuleVersionCreate(BaseModel):
    code: str
    title: str
    severity: str = "error"
    applies_to: str
    dsl: dict
    remediation: str | None = None
    enabled: bool = True


class RuleVersionRead(IdentifiedModel):
    district_id: UUID | None
    code: str
    title: str
    severity: str
    applies_to: str
    dsl: dict
    remediation: str | None
    enabled: bool


class RuleRunCreate(BaseModel):
    rule_version_id: UUID | None = None
    initiated_by: str | None = None
    scope: dict | None = None


class RuleRunRead(IdentifiedModel):
    district_id: UUID
    rule_version_id: UUID | None
    initiated_by: str | None
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    scope: dict | None


class RuleResultRead(IdentifiedModel):
    rule_run_id: UUID
    district_id: UUID
    school_id: UUID | None
    entity_type: str
    entity_id: UUID | None
    severity: str
    status: str
    message: str
    details: dict | None
