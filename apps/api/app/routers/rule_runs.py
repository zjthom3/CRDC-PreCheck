from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.db.models import District, RuleRun, RuleRunStatusEnum, RuleVersion
from apps.api.app.db.session import get_session
from apps.api.app.schemas import RuleRunCreate, RuleRunRead
from apps.worker.worker.tasks import process_rule_run

router = APIRouter(prefix="/rules/runs", tags=["rules"])


@router.get("", response_model=list[RuleRunRead])
def list_rule_runs(
    district: District = Depends(get_district), session: Session = Depends(get_session)
) -> list[RuleRun]:
    result = session.execute(
        select(RuleRun)
        .where(RuleRun.district_id == district.id)
        .order_by(RuleRun.created_at.desc())
    )
    return list(result.scalars())


@router.post("", response_model=RuleRunRead, status_code=status.HTTP_202_ACCEPTED)
def create_rule_run(
    payload: RuleRunCreate,
    district: District = Depends(get_district),
    session: Session = Depends(get_session),
) -> RuleRun:
    rule_version_id: UUID | None = payload.rule_version_id
    if rule_version_id:
        rule_version = session.get(RuleVersion, rule_version_id)
        if rule_version is None or (
            rule_version.district_id not in (None, district.id)
        ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found")
    else:
        rule_version = None

    rule_run = RuleRun(
        district_id=district.id,
        rule_version_id=rule_version.id if rule_version else None,
        initiated_by=payload.initiated_by,
        status=RuleRunStatusEnum.pending,
        scope=payload.scope,
    )
    session.add(rule_run)
    session.commit()
    session.refresh(rule_run)

    try:
        process_rule_run.delay(str(rule_run.id))
    except Exception:  # pragma: no cover - fallback for local dev without broker
        process_rule_run(str(rule_run.id))
    return rule_run
