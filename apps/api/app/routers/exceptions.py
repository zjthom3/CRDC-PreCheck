from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.dependencies.auth import get_current_user
from apps.api.app.db.models import (
    ExceptionMemo,
    ExceptionRecord,
    ExceptionStatusEnum,
    RuleResult,
    UserAccount,
)
from apps.api.app.db.session import get_session
from apps.api.app.schemas import (
    ExceptionCreate,
    ExceptionMemoCreate,
    ExceptionMemoRead,
    ExceptionRead,
    ExceptionUpdate,
)

router = APIRouter(prefix="/exceptions", tags=["exceptions"])


@router.get("", response_model=list[ExceptionRead])
def list_exceptions(district=Depends(get_district), session: Session = Depends(get_session)) -> list[ExceptionRecord]:
    records = (
        session.execute(
            select(ExceptionRecord).where(ExceptionRecord.district_id == district.id).order_by(ExceptionRecord.created_at.desc())
        )
        .scalars()
        .all()
    )
    return records


@router.post("", response_model=ExceptionRead, status_code=status.HTTP_201_CREATED)
def create_exception(
    payload: ExceptionCreate,
    district=Depends(get_district),
    current_user: UserAccount | None = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ExceptionRecord:
    rule_result = session.execute(
        select(RuleResult).where(RuleResult.id == payload.rule_result_id, RuleResult.district_id == district.id)
    ).scalar_one_or_none()
    if rule_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule result not found")

    existing = session.execute(
        select(ExceptionRecord).where(ExceptionRecord.rule_result_id == rule_result.id)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Exception already exists for this result")

    exception = ExceptionRecord(
        district_id=district.id,
        rule_result_id=rule_result.id,
        owner_user_id=current_user.id if current_user else None,
        rationale=payload.rationale,
        due_date=payload.due_date,
        status=ExceptionStatusEnum.open,
    )
    session.add(exception)
    session.commit()
    session.refresh(exception)
    return exception


@router.patch("/{exception_id}", response_model=ExceptionRead)
def update_exception(
    exception_id: UUID,
    payload: ExceptionUpdate,
    district=Depends(get_district),
    current_user: UserAccount | None = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ExceptionRecord:
    exception = session.execute(
        select(ExceptionRecord).where(ExceptionRecord.id == exception_id, ExceptionRecord.district_id == district.id)
    ).scalar_one_or_none()
    if exception is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exception not found")

    if payload.status:
        try:
            exception.status = ExceptionStatusEnum(payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value") from exc

    if payload.owner_user_id is not None:
        owner = session.get(UserAccount, payload.owner_user_id)
        if owner is None or owner.district_id != district.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
        exception.owner_user_id = owner.id

    if payload.rationale is not None:
        exception.rationale = payload.rationale

    if payload.due_date is not None:
        exception.due_date = payload.due_date

    if payload.approved:
        exception.approval_user_id = current_user.id if current_user else None
        exception.approved_at = datetime.utcnow()
        exception.status = ExceptionStatusEnum.resolved

    session.commit()
    session.refresh(exception)
    return exception


@router.post("/{exception_id}/memo", response_model=ExceptionMemoRead, status_code=status.HTTP_201_CREATED)
def create_exception_memo(
    exception_id: UUID,
    payload: ExceptionMemoCreate,
    district=Depends(get_district),
    session: Session = Depends(get_session),
) -> ExceptionMemo:
    exception = session.execute(
        select(ExceptionRecord).where(ExceptionRecord.id == exception_id, ExceptionRecord.district_id == district.id)
    ).scalar_one_or_none()
    if exception is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exception not found")

    memo = ExceptionMemo(
        district_id=district.id,
        exception_id=exception.id,
        title=payload.title,
        body_md=payload.body_md,
        generated_by=payload.generated_by,
    )
    session.add(memo)
    session.commit()
    session.refresh(memo)
    return memo


@router.get("/{exception_id}/memo", response_model=list[ExceptionMemoRead])
def list_exception_memos(exception_id: UUID, district=Depends(get_district), session: Session = Depends(get_session)) -> list[ExceptionMemo]:
    memos = (
        session.execute(
            select(ExceptionMemo)
            .where(ExceptionMemo.district_id == district.id, ExceptionMemo.exception_id == exception_id)
            .order_by(ExceptionMemo.created_at.desc())
        )
        .scalars()
        .all()
    )
    return memos
