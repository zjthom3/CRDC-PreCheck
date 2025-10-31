import csv
import io

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.dependencies.auth import require_roles
from apps.api.app.db.models import ExceptionRecord, RuleResult, UserAccount, UserRoleEnum
from apps.api.app.db.session import get_session
from apps.api.app.services.audit import write_audit_log

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/exceptions.csv")
def export_exceptions(
    district=Depends(get_district),
    user: UserAccount = Depends(require_roles(UserRoleEnum.admin, UserRoleEnum.reviewer)),
    session: Session = Depends(get_session),
) -> Response:
    results = (
        session.execute(
            select(ExceptionRecord, RuleResult)
            .join(RuleResult, RuleResult.id == ExceptionRecord.rule_result_id)
            .where(ExceptionRecord.district_id == district.id)
        )
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "exception_id",
        "rule_result_id",
        "status",
        "rationale",
        "due_date",
        "severity",
        "rule_message",
    ])

    for exc, result in results:
        writer.writerow(
            [
                exc.id,
                exc.rule_result_id,
                exc.status.value,
                exc.rationale or "",
                exc.due_date.isoformat() if exc.due_date else "",
                result.severity.value,
                result.message,
            ]
        )

    buffer.seek(0)
    response = Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=exceptions.csv"},
    )
    write_audit_log(
        session,
        district_id=district.id,
        user_id=user.id,
        action="EXPORT_EXCEPTIONS",
        entity_type="ExceptionRecord",
        entity_id=None,
        details={"rows": len(results)},
    )
    session.commit()
    return response
