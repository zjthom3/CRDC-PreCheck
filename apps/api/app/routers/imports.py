import csv
import io
import json
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from apps.api.app.db.models import IngestBatch, IngestStatusEnum
from apps.api.app.db.session import get_session
from apps.api.app.dependencies import get_district
from apps.api.app.schemas import CsvImportResult, StudentCsvMapping
from apps.api.app.services.students import upsert_student

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/students/csv", response_model=CsvImportResult, status_code=status.HTTP_202_ACCEPTED)
async def import_students_csv(
    file: UploadFile = File(..., description="CSV containing student records"),
    mapping: str = Form(..., description="JSON mapping of student fields to CSV columns"),
    district=Depends(get_district),
    session: Session = Depends(get_session),
) -> CsvImportResult:
    try:
        mapping_model = StudentCsvMapping.model_validate_json(mapping)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mapping JSON") from exc

    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file has no header row")

    missing_columns: list[str] = [
        column
        for column in mapping_model.model_dump().values()
        if column and column not in reader.fieldnames
    ]
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV missing required column(s): {', '.join(missing_columns)}",
        )

    batch = IngestBatch(
        district_id=district.id,
        table_name="student",
        status=IngestStatusEnum.pending,
    )
    session.add(batch)
    session.commit()

    processed = created = updated = 0
    errors: list[str] = []

    for index, row in enumerate(reader, start=1):
        try:
            payload = _build_student_payload(row, mapping_model)
            _, student_created = upsert_student(session, district_id=district.id, **payload)
            processed += 1
            if student_created:
                created += 1
            else:
                updated += 1
        except Exception as exc:  # pragma: no cover - defensive logging branch
            session.rollback()
            session.add(batch)
            errors.append(f"Row {index}: {exc}")
        else:
            session.commit()

    batch.rows_ingested = processed
    batch.status = IngestStatusEnum.success if not errors else IngestStatusEnum.failed
    session.commit()

    return CsvImportResult(
        rows_processed=processed,
        students_created=created,
        students_updated=updated,
        errors=errors,
        ingest_batch_id=str(batch.id),
    )


def _build_student_payload(row: dict[str, Any], mapping: StudentCsvMapping) -> dict[str, Any]:
    grade_value = row[mapping.grade_level].strip()
    try:
        grade_level = int(grade_value)
    except ValueError as exc:
        raise ValueError(f"Grade level '{grade_value}' is not a valid integer") from exc

    enrollment_status = (
        row[mapping.enrollment_status].strip() if mapping.enrollment_status else "active"
    )
    ell_raw = row[mapping.ell_status].strip().lower() if mapping.ell_status else None
    idea_raw = row[mapping.idea_flag].strip().lower() if mapping.idea_flag else None

    def _interpret_flag(value: str | None) -> bool | None:
        if value is None:
            return None
        return value in {"1", "true", "yes", "y"}

    return {
        "sis_id": row[mapping.sis_id].strip(),
        "first_name": row[mapping.first_name].strip(),
        "last_name": row[mapping.last_name].strip(),
        "grade_level": grade_level,
        "school_name": row[mapping.school_name].strip(),
        "enrollment_status": enrollment_status or "active",
        "ell_status": _interpret_flag(ell_raw),
        "idea_flag": _interpret_flag(idea_raw),
    }
