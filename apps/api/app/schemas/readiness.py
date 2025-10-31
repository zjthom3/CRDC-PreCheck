from uuid import UUID

from pydantic import BaseModel


class ReadinessDetail(BaseModel):
    school_id: UUID | None
    school_name: str | None
    category: str
    score: int
    open_errors: int
    open_warnings: int


class ReadinessResponse(BaseModel):
    items: list[ReadinessDetail]
