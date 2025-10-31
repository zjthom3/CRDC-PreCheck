from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Shared configuration to support ORM serialization."""

    model_config = ConfigDict(from_attributes=True)


class TimestampFields(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IdentifiedModel(ORMModel, TimestampFields):
    id: UUID
