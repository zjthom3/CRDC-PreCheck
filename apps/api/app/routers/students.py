from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.db.models import District, Student
from apps.api.app.db.session import get_session
from apps.api.app.schemas import StudentCreate, StudentRead

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentRead])
def list_students(
    school_id: UUID | None = Query(default=None),
    district: District = Depends(get_district),
    session: Session = Depends(get_session),
) -> list[Student]:
    query = select(Student).where(Student.district_id == district.id)
    if school_id is not None:
        query = query.where(Student.school_id == school_id)

    result = session.execute(query.order_by(Student.last_name, Student.first_name))
    return list(result.scalars())


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    district: District = Depends(get_district),
    session: Session = Depends(get_session),
) -> Student:
    student = Student(district_id=district.id, **payload.model_dump())
    session.add(student)
    session.commit()
    session.refresh(student)
    return student
