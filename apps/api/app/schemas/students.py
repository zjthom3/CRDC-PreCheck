from datetime import date
from uuid import UUID

from pydantic import BaseModel

from .common import IdentifiedModel


class StudentCreate(BaseModel):
    school_id: UUID
    sis_id: str
    first_name: str
    last_name: str
    grade_level: int
    ell_status: bool = False
    idea_flag: bool = False
    enrollment_status: str = "active"
    enrollment_start: date | None = None
    enrollment_end: date | None = None


class StudentRead(IdentifiedModel):
    district_id: UUID
    school_id: UUID
    sis_id: str
    first_name: str
    last_name: str
    grade_level: int
    ell_status: bool
    idea_flag: bool
    enrollment_status: str
    enrollment_start: date | None
    enrollment_end: date | None
