from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.db.models import UserAccount, UserRoleEnum
from apps.api.app.db.session import get_session


def get_current_user(
    authorization: str | None = Header(default=None, convert_underscores=False),
    session: Session = Depends(get_session),
) -> UserAccount | None:
    """Return the authenticated user, if an access token is supplied."""

    if not authorization:
        return None

    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header") from exc

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token scheme")

    user = session.execute(select(UserAccount).where(UserAccount.api_token == token)).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive token")

    return user


def require_user(user: UserAccount | None = Depends(get_current_user)) -> UserAccount:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def require_roles(*roles: UserRoleEnum):
    def dependency(user: UserAccount = Depends(require_user)) -> UserAccount:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


__all__ = ["get_current_user", "require_user", "require_roles"]
