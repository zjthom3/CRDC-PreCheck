from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.db.models import District, RuleResult
from apps.api.app.db.session import get_session
from apps.api.app.schemas import RuleResultRead

router = APIRouter(prefix="/rules/results", tags=["rules"])


@router.get("", response_model=list[RuleResultRead])
def list_rule_results(
    rule_run_id: UUID | None = Query(default=None),
    district: District = Depends(get_district),
    session: Session = Depends(get_session),
) -> list[RuleResult]:
    query = select(RuleResult).where(RuleResult.district_id == district.id)
    if rule_run_id is not None:
        query = query.where(RuleResult.rule_run_id == rule_run_id)

    result = session.execute(query.order_by(RuleResult.created_at.desc()))
    return list(result.scalars())
