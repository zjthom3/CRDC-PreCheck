from uuid import UUID

from pydantic import BaseModel

from .common import IdentifiedModel


class SchoolCreate(BaseModel):
    name: str
    level: str | None = None
    nces_id: str | None = None


class SchoolRead(IdentifiedModel):
    district_id: UUID
    name: str
    level: str | None
    nces_id: str | None
