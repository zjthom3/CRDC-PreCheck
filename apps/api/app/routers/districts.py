from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.db.models import District
from apps.api.app.db.session import get_session
from apps.api.app.schemas import DistrictCreate, DistrictRead

router = APIRouter(prefix="/districts", tags=["districts"])


@router.get("", response_model=list[DistrictRead])
def list_districts(session: Session = Depends(get_session)) -> list[District]:
    """Return all districts ordered by name."""

    result = session.execute(select(District).order_by(District.name))
    return list(result.scalars())


@router.post("", response_model=DistrictRead, status_code=status.HTTP_201_CREATED)
def create_district(
    payload: DistrictCreate, session: Session = Depends(get_session)
) -> District:
    """Create a new district tenant."""

    district = District(name=payload.name, timezone=payload.timezone, nces_id=payload.nces_id)
    session.add(district)
    session.commit()
    session.refresh(district)
    return district
