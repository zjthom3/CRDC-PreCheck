from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.db.models import District, RuleSeverityEnum, RuleVersion
from apps.api.app.db.session import get_session
from apps.api.app.schemas import RuleVersionCreate, RuleVersionRead

router = APIRouter(prefix="/rules/versions", tags=["rules"])


@router.get("", response_model=list[RuleVersionRead])
def list_rule_versions(
    district: District = Depends(get_district), session: Session = Depends(get_session)
) -> list[RuleVersion]:
    result = session.execute(
        select(RuleVersion)
        .where((RuleVersion.district_id == district.id) | (RuleVersion.district_id.is_(None)))
        .order_by(RuleVersion.code)
    )
    return list(result.scalars())


@router.post("", response_model=RuleVersionRead, status_code=status.HTTP_201_CREATED)
def create_rule_version(
    payload: RuleVersionCreate,
    district: District = Depends(get_district),
    session: Session = Depends(get_session),
) -> RuleVersion:
    rule_version = RuleVersion(
        district_id=district.id,
        code=payload.code,
        title=payload.title,
        severity=RuleSeverityEnum(payload.severity),
        applies_to=payload.applies_to,
        dsl=payload.dsl,
        remediation=payload.remediation,
        enabled=payload.enabled,
    )
    session.add(rule_version)
    session.commit()
    session.refresh(rule_version)
    return rule_version
