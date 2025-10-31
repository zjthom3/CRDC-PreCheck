from pydantic import BaseModel, ConfigDict

from .common import IdentifiedModel


class DistrictCreate(BaseModel):
    name: str
    timezone: str = "America/Chicago"
    nces_id: str | None = None


class DistrictRead(IdentifiedModel):
    name: str
    timezone: str
    nces_id: str | None

    model_config = ConfigDict(from_attributes=True)
