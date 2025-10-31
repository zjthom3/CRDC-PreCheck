from collections import defaultdict
from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.db.models import ReadinessScore, RuleResult, School
from apps.api.app.db.session import get_session
from apps.api.app.schemas import ReadinessDetail, ReadinessResponse

router = APIRouter(prefix="/readiness", tags=["readiness"])


@router.get("", response_model=ReadinessResponse)
def get_readiness(district=Depends(get_district), session: Session = Depends(get_session)) -> ReadinessResponse:
    readiness_rows = (
        session.execute(
            select(ReadinessScore).where(ReadinessScore.district_id == district.id)
        )
        .scalars()
        .all()
    )

    if readiness_rows:
        items = [
            ReadinessDetail(
                school_id=score.school_id,
                school_name=session.get(School, score.school_id).name if score.school_id else "District",
                category=score.category,
                score=score.score,
                open_errors=0,
                open_warnings=0,
            )
            for score in readiness_rows
        ]
        return ReadinessResponse(items=items)

    results = (
        session.execute(
            select(RuleResult, School.name)
            .outerjoin(School, RuleResult.school_id == School.id)
            .where(RuleResult.district_id == district.id, RuleResult.status == "open")
        )
        .all()
    )

    totals: Dict[UUID | None, dict[str, int]] = defaultdict(lambda: {"errors": 0, "warnings": 0})
    school_names: Dict[UUID | None, str | None] = {}

    for rule_result, school_name in results:
        school_id = rule_result.school_id
        school_names[school_id] = school_name
        if rule_result.severity.value == "error":
            totals[school_id]["errors"] += 1
        elif rule_result.severity.value == "warning":
            totals[school_id]["warnings"] += 1

    items: list[ReadinessDetail] = []
    for school_id, counts in totals.items():
        score = max(0, 100 - counts["errors"] * 20 - counts["warnings"] * 10)
        items.append(
            ReadinessDetail(
                school_id=school_id,
                school_name=school_names.get(school_id) if school_id else "District",
                category="Overall",
                score=score,
                open_errors=counts["errors"],
                open_warnings=counts["warnings"],
            )
        )

    return ReadinessResponse(items=items)
