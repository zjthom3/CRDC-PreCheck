from datetime import datetime
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.db.models import UserAccount, UserRoleEnum
from apps.api.app.db.session import get_session
from apps.api.app.dependencies import get_district
from apps.api.app.dependencies.auth import get_current_user, require_user
from apps.api.app.schemas import AuthResponse, SSOLoginRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sso", response_model=AuthResponse)
def sso_login(
    payload: SSOLoginRequest,
    district=Depends(get_district),
    session: Session = Depends(get_session),
) -> AuthResponse:
    user = session.execute(
        select(UserAccount).where(
            UserAccount.district_id == district.id,
            UserAccount.sso_provider == payload.provider,
            UserAccount.sso_subject == payload.subject,
        )
    ).scalar_one_or_none()

    if user is None:
        user = UserAccount(
            district_id=district.id,
            email=payload.email,
            display_name=payload.display_name,
            role=UserRoleEnum.admin,
            api_token=token_urlsafe(32),
            sso_provider=payload.provider,
            sso_subject=payload.subject,
            is_active=True,
        )
        session.add(user)
    else:
        user.email = payload.email
        user.display_name = payload.display_name
        if not user.api_token:
            user.api_token = token_urlsafe(32)

    user.last_login_at = datetime.utcnow()
    session.commit()
    session.refresh(user)

    return AuthResponse(token=user.api_token, user=_serialize_user(user))


@router.get("/me", response_model=AuthResponse)
def get_me(user=Depends(require_user)) -> AuthResponse:
    return AuthResponse(token=user.api_token, user=_serialize_user(user))


def _serialize_user(user: UserAccount) -> UserRead:
    return UserRead(
        id=user.id,
        district_id=user.district_id,
        email=user.email,
        display_name=user.display_name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        is_active=user.is_active,
        sso_provider=user.sso_provider,
        sso_subject=user.sso_subject,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
