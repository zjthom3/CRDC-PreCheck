from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.db.models import AuditLog


def write_audit_log(
    session: Session,
    *,
    district_id: UUID,
    user_id: UUID | None,
    action: str,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    log_entry = AuditLog(
        district_id=district_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata,
    )
    session.add(log_entry)
    session.flush()
