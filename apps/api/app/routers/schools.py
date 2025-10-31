from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.db.models import District, School
from apps.api.app.db.session import get_session
from apps.api.app.schemas import SchoolCreate, SchoolRead

router = APIRouter(prefix="/schools", tags=["schools"])


@router.get("", response_model=list[SchoolRead])
def list_schools(
    district: District = Depends(get_district), session: Session = Depends(get_session)
) -> list[School]:
    result = session.execute(
        select(School).where(School.district_id == district.id).order_by(School.name)
    )
    return list(result.scalars())


@router.post("", response_model=SchoolRead, status_code=status.HTTP_201_CREATED)
def create_school(
    payload: SchoolCreate,
    district: District = Depends(get_district),
    session: Session = Depends(get_session),
) -> School:
    school = School(
        district_id=district.id,
        name=payload.name,
        level=payload.level,
        nces_id=payload.nces_id,
    )
    session.add(school)
    session.commit()
    session.refresh(school)
    return school
