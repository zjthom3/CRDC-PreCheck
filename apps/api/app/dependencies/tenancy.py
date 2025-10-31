from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from apps.api.app.db.models import District, UserAccount
from apps.api.app.db.session import get_session
from apps.api.app.dependencies.auth import get_current_user


def get_district(
    x_district_id: str | None = Header(default=None, alias="X-District-ID"),
    current_user: UserAccount | None = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> District:
    """Resolve the active district from the request header or authenticated user."""

    district_uuid: UUID | None = None
    if current_user is not None:
        district_uuid = current_user.district_id
    elif x_district_id:
        try:
            district_uuid = UUID(x_district_id)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid district id"
            ) from exc
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context required via X-District-ID or authorization token",
        )

    district = session.get(District, district_uuid)
    if district is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")

    return district


def get_tenant_session(
    session: Session = Depends(get_session), district: District = Depends(get_district)
) -> Session:
    """Return the session after verifying tenant context.

    Future RLS policies can hook in here to scope queries.
    """

    # Placeholder for future row-level security enforcement per tenant.
    return session


__all__ = ["get_district", "get_tenant_session"]
