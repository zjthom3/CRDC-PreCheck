from typing import Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.app.db.models import School, Student


def upsert_student(
    session: Session,
    *,
    district_id: UUID,
    sis_id: str,
    first_name: str,
    last_name: str,
    grade_level: int,
    enrollment_status: str,
    school_name: str,
    ell_status: bool | None = None,
    idea_flag: bool | None = None,
) -> Tuple[Student, bool]:
    """Create or update a student record and return (student, created)."""

    school = session.execute(
        select(School).where(
            School.district_id == district_id,
            func.lower(School.name) == school_name.lower(),
        )
    ).scalar_one_or_none()
    if school is None:
        school = School(district_id=district_id, name=school_name)
        session.add(school)
        session.flush()

    student = session.execute(
        select(Student).where(Student.district_id == district_id, Student.sis_id == sis_id)
    ).scalar_one_or_none()

    created = False
    if student is None:
        student = Student(
            district_id=district_id,
            school_id=school.id,
            sis_id=sis_id,
            first_name=first_name,
            last_name=last_name,
            grade_level=grade_level,
            enrollment_status=enrollment_status,
            ell_status=ell_status or False,
            idea_flag=idea_flag or False,
        )
        session.add(student)
        created = True
    else:
        student.school_id = school.id
        student.first_name = first_name
        student.last_name = last_name
        student.grade_level = grade_level
        student.enrollment_status = enrollment_status
        if ell_status is not None:
            student.ell_status = ell_status
        if idea_flag is not None:
            student.idea_flag = idea_flag

    session.flush()
    return student, created
