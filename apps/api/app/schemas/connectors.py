from pydantic import BaseModel


class SyncTriggerResponse(BaseModel):
    status: str
    task_id: str | None = None
