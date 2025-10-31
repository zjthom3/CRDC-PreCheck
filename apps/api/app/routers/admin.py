from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.dependencies.auth import require_roles
from apps.api.app.db.models import Connector, RuleRun, SyncJob, UserAccount, UserRoleEnum
from apps.api.app.db.session import get_session

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
def get_health(
    district=Depends(get_district),
    user: UserAccount = Depends(require_roles(UserRoleEnum.admin)),
    session: Session = Depends(get_session),
) -> dict:
    connectors = (
        session.execute(
            select(Connector).where(Connector.district_id == district.id)
        )
        .scalars()
        .all()
    )

    last_run = session.execute(
        select(RuleRun)
        .where(RuleRun.district_id == district.id)
        .order_by(RuleRun.created_at.desc())
    ).scalar_one_or_none()

    latest_sync = session.execute(
        select(func.max(SyncJob.finished_at))
        .join(Connector, SyncJob.connector_id == Connector.id)
        .where(Connector.district_id == district.id)
    ).scalar_one_or_none()

    return {
        "connectors": [
            {
                "id": str(connector.id),
                "status": connector.status.value if hasattr(connector.status, "value") else connector.status,
                "last_sync_at": connector.last_sync_at.isoformat() if connector.last_sync_at else None,
            }
            for connector in connectors
        ],
        "last_validation": last_run.finished_at.isoformat() if last_run and last_run.finished_at else None,
        "latest_sync_finished_at": latest_sync.isoformat() if isinstance(latest_sync, datetime) else None,
    }
