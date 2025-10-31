from uuid import UUID

from pydantic import BaseModel

from .common import IdentifiedModel


class EvidencePacketCreate(BaseModel):
    name: str
    description: str | None = None
    exception_ids: list[UUID] = []


class EvidencePacketRead(IdentifiedModel):
    district_id: UUID
    name: str
    description: str | None
    zip_url: str | None
    sha256: str | None
    created_by: UUID | None
