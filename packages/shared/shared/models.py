from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TenantScopedModel(BaseModel):
    """Base model shared by API and worker for tenant-aware data."""

    district_id: UUID = Field(description="Tenant identifier scoped via RLS.")
    created_at: datetime = Field(description="Creation timestamp in UTC.")
    updated_at: datetime = Field(description="Last update timestamp in UTC.")

    class Config:
        orm_mode = True
