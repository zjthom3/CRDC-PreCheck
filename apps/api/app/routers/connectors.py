from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.dependencies.auth import require_roles
from apps.api.app.db.models import UserRoleEnum
from apps.api.app.db.session import get_session
from apps.api.app.schemas import SyncTriggerResponse
from apps.api.app.services.audit import write_audit_log
from apps.worker.worker.tasks import sync_powerschool

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.post("/powerschool/sync", response_model=SyncTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_powerschool_sync(
    district=Depends(get_district),
    user=Depends(require_roles(UserRoleEnum.admin, UserRoleEnum.data_engineer)),
    session: Session = Depends(get_session),
) -> SyncTriggerResponse:
    """Trigger a background sync for the PowerSchool connector."""

    try:
        async_result = sync_powerschool.delay(str(district.id))
        task_id = async_result.id
    except Exception:  # pragma: no cover - fallback when broker unavailable
        sync_powerschool(str(district.id))
        task_id = None

    write_audit_log(
        session,
        district_id=district.id,
        user_id=user.id,
        action="CONNECTOR_SYNC",
        entity_type="Connector",
        entity_id=None,
        details={"provider": "powerschool", "task_id": task_id},
    )
    session.commit()

    return SyncTriggerResponse(status="queued", task_id=task_id)
