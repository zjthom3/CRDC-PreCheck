import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from uuid import UUID
from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.dependencies import get_district
from apps.api.app.dependencies.auth import require_roles
from apps.api.app.db.models import (
    EvidenceItem,
    EvidencePacket,
    ExceptionRecord,
    EvidenceKindEnum,
    UserAccount,
    UserRoleEnum,
)
from apps.api.app.db.session import get_session
from apps.api.app.schemas import EvidencePacketCreate, EvidencePacketRead
from apps.api.app.services.audit import write_audit_log

STORAGE_ROOT = Path(os.getenv("EVIDENCE_STORAGE", "storage/evidence"))

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/packets", response_model=EvidencePacketRead, status_code=status.HTTP_201_CREATED)
def create_packet(
    payload: EvidencePacketCreate,
    district=Depends(get_district),
    user: UserAccount = Depends(require_roles(UserRoleEnum.admin, UserRoleEnum.reviewer)),
    session: Session = Depends(get_session),
) -> EvidencePacket:
    exceptions = (
        session.execute(
            select(ExceptionRecord).where(
                ExceptionRecord.district_id == district.id,
                ExceptionRecord.id.in_(payload.exception_ids or []),
            )
        )
        .scalars()
        .all()
    )

    if payload.exception_ids and len(exceptions) != len(payload.exception_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more exceptions not found")

    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"packet-{district.id}-{timestamp}.zip"
    zip_path = STORAGE_ROOT / filename

    packet_summary = {
        "name": payload.name,
        "description": payload.description,
        "generated_at": datetime.utcnow().isoformat(),
        "exceptions": [
            {
                "id": str(exc.id),
                "rule_result_id": str(exc.rule_result_id),
                "status": exc.status.value,
                "rationale": exc.rationale,
                "due_date": exc.due_date.isoformat() if exc.due_date else None,
            }
            for exc in exceptions
        ],
    }

    with ZipFile(zip_path, "w") as zf:
        zf.writestr("packet.json", json.dumps(packet_summary, indent=2))

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    packet = EvidencePacket(
        district_id=district.id,
        name=payload.name,
        description=payload.description,
        zip_url=str(zip_path),
        sha256=sha256,
        created_by=user.id if user else None,
    )
    session.add(packet)
    session.commit()
    session.refresh(packet)

    for exc in exceptions:
        item = EvidenceItem(
            district_id=district.id,
            packet_id=packet.id,
            exception_id=exc.id,
            kind=EvidenceKindEnum.export,
            title=f"Exception {exc.id}",
            uri=f"{zip_path}#exception-{exc.id}",
        )
        session.add(item)

    session.commit()
    session.refresh(packet)

    write_audit_log(
        session,
        district_id=district.id,
        user_id=user.id,
        action="EVIDENCE_PACKET_CREATE",
        entity_type="EvidencePacket",
        entity_id=packet.id,
        metadata={"exceptions": [str(exc.id) for exc in exceptions]},
    )
    return packet
