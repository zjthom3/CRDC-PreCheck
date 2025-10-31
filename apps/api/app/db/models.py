from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import GUID


class RuleRunStatusEnum(str, PyEnum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class RuleResultStatusEnum(str, PyEnum):
    open = "open"
    resolved = "resolved"
    deferred = "deferred"
    accepted = "accepted"


class RuleSeverityEnum(str, PyEnum):
    error = "error"
    warning = "warning"
    info = "info"


class UserRoleEnum(str, PyEnum):
    admin = "admin"
    data_engineer = "data_engineer"
    reviewer = "reviewer"
    readonly = "readonly"


class ConnectorStatusEnum(str, PyEnum):
    healthy = "healthy"
    degraded = "degraded"
    error = "error"


class AuthMethodEnum(str, PyEnum):
    oauth = "oauth"
    token = "token"
    csv_upload = "csv_upload"


class SyncStatusEnum(str, PyEnum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class IngestStatusEnum(str, PyEnum):
    pending = "pending"
    success = "success"
    failed = "failed"


class ExceptionStatusEnum(str, PyEnum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    wont_fix = "won't_fix"


class EvidenceKindEnum(str, PyEnum):
    csv = "csv"
    screenshot = "screenshot"
    policy = "policy"
    export = "export"


RuleRunStatus = Enum(RuleRunStatusEnum, name="rule_run_status", native_enum=False)
RuleResultStatus = Enum(RuleResultStatusEnum, name="rule_result_status", native_enum=False)
RuleSeverity = Enum(RuleSeverityEnum, name="rule_severity", native_enum=False)
UserRole = Enum(UserRoleEnum, name="user_role", native_enum=False)
ConnectorStatus = Enum(ConnectorStatusEnum, name="connector_status", native_enum=False)
AuthMethod = Enum(AuthMethodEnum, name="auth_method", native_enum=False)
SyncStatus = Enum(SyncStatusEnum, name="sync_status", native_enum=False)
IngestStatus = Enum(IngestStatusEnum, name="ingest_status", native_enum=False)
ExceptionStatus = Enum(ExceptionStatusEnum, name="exception_status", native_enum=False)
EvidenceKind = Enum(EvidenceKindEnum, name="evidence_kind", native_enum=False)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class District(Base, TimestampMixin):
    __tablename__ = "district"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    nces_id: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="America/Chicago")

    schools: Mapped[list["School"]] = relationship(back_populates="district", cascade="all, delete")
    rule_versions: Mapped[list["RuleVersion"]] = relationship(
        back_populates="district", cascade="all, delete"
    )


class School(Base, TimestampMixin):
    __tablename__ = "school"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    nces_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str | None] = mapped_column(String(64), nullable=True)

    district: Mapped["District"] = relationship(back_populates="schools")
    students: Mapped[list["Student"]] = relationship(back_populates="school", cascade="all, delete")


class Student(Base, TimestampMixin):
    __tablename__ = "student"
    __table_args__ = (
        UniqueConstraint("district_id", "sis_id", name="uq_student_district_sis"),
    )

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    school_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("school.id", ondelete="CASCADE"), nullable=False)
    sis_id: Mapped[str] = mapped_column(String(64), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False)
    ell_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    idea_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enrollment_status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    enrollment_start: Mapped[Date] = mapped_column(Date, nullable=True)
    enrollment_end: Mapped[Date] = mapped_column(Date, nullable=True)

    district: Mapped["District"] = relationship()
    school: Mapped["School"] = relationship(back_populates="students")


class RuleVersion(Base, TimestampMixin):
    __tablename__ = "rule_version"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("district.id", ondelete="SET NULL"), nullable=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[RuleSeverityEnum] = mapped_column(
        RuleSeverity, nullable=False, default=RuleSeverityEnum.error
    )
    applies_to: Mapped[str] = mapped_column(String(64), nullable=False)
    dsl: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    remediation: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    district: Mapped["District"] = relationship(back_populates="rule_versions")
    rule_runs: Mapped[list["RuleRun"]] = relationship(back_populates="rule_version")


class RuleRun(Base, TimestampMixin):
    __tablename__ = "rule_run"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    rule_version_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("rule_version.id", ondelete="SET NULL"), nullable=True
    )
    initiated_by: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[RuleRunStatusEnum] = mapped_column(
        RuleRunStatus, nullable=False, default=RuleRunStatusEnum.pending
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scope: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    rule_version: Mapped["RuleVersion"] = relationship(back_populates="rule_runs")
    results: Mapped[list["RuleResult"]] = relationship(
        back_populates="rule_run", cascade="all, delete-orphan"
    )


class RuleResult(Base, TimestampMixin):
    __tablename__ = "rule_result"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    rule_run_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("rule_run.id", ondelete="CASCADE"), nullable=False
    )
    district_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False
    )
    school_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("school.id", ondelete="SET NULL"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    severity: Mapped[RuleSeverityEnum] = mapped_column(
        RuleSeverity, nullable=False, default=RuleSeverityEnum.error
    )
    status: Mapped[RuleResultStatusEnum] = mapped_column(
        RuleResultStatus, nullable=False, default=RuleResultStatusEnum.open
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    rule_run: Mapped["RuleRun"] = relationship(back_populates="results")
    school: Mapped["School"] = relationship()


class UserAccount(Base, TimestampMixin):
    __tablename__ = "user_account"
    __table_args__ = (
        UniqueConstraint("district_id", "email", name="uq_user_district_email"),
        UniqueConstraint("api_token", name="uq_user_api_token"),
        UniqueConstraint("sso_provider", "sso_subject", name="uq_user_sso"),
    )

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(UserRole, nullable=False, default=UserRoleEnum.admin)
    api_token: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sso_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sso_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    district: Mapped["District"] = relationship()


class SourceSystem(Base, TimestampMixin):
    __tablename__ = "source_system"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    district: Mapped["District"] = relationship()
    connectors: Mapped[list["Connector"]] = relationship(back_populates="source_system")


class Connector(Base, TimestampMixin):
    __tablename__ = "connector"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    source_system_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("source_system.id", ondelete="CASCADE"), nullable=False
    )
    auth_method: Mapped[AuthMethodEnum] = mapped_column(AuthMethod, nullable=False)
    status: Mapped[ConnectorStatusEnum] = mapped_column(
        ConnectorStatus, nullable=False, default=ConnectorStatusEnum.healthy
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    district: Mapped["District"] = relationship()
    source_system: Mapped["SourceSystem"] = relationship(back_populates="connectors")
    sync_jobs: Mapped[list["SyncJob"]] = relationship(back_populates="connector", cascade="all, delete-orphan")


class SyncJob(Base, TimestampMixin):
    __tablename__ = "sync_job"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    connector_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("connector.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[SyncStatusEnum] = mapped_column(SyncStatus, nullable=False, default=SyncStatusEnum.queued)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text)

    connector: Mapped["Connector"] = relationship(back_populates="sync_jobs")
    ingest_batches: Mapped[list["IngestBatch"]] = relationship(
        back_populates="sync_job", cascade="all, delete-orphan"
    )


class IngestBatch(Base, TimestampMixin):
    __tablename__ = "ingest_batch"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    source_system_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("source_system.id", ondelete="SET NULL"), nullable=True
    )
    sync_job_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("sync_job.id", ondelete="SET NULL"), nullable=True
    )
    table_name: Mapped[str] = mapped_column(String(64), nullable=False)
    rows_ingested: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[IngestStatusEnum] = mapped_column(
        IngestStatus, nullable=False, default=IngestStatusEnum.pending
    )
    source_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    district: Mapped["District"] = relationship()
    source_system: Mapped["SourceSystem"] = relationship()
    sync_job: Mapped["SyncJob"] = relationship(back_populates="ingest_batches")


class ExceptionRecord(Base, TimestampMixin):
    __tablename__ = "exception_record"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    rule_result_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("rule_result.id", ondelete="CASCADE"), nullable=False
    )
    owner_user_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("user_account.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ExceptionStatusEnum] = mapped_column(
        ExceptionStatus, nullable=False, default=ExceptionStatusEnum.open
    )
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    approval_user_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("user_account.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    district: Mapped["District"] = relationship()
    rule_result: Mapped["RuleResult"] = relationship()
    owner: Mapped["UserAccount | None"] = relationship(foreign_keys=[owner_user_id])
    approver: Mapped["UserAccount | None"] = relationship(foreign_keys=[approval_user_id])


class EvidencePacket(Base, TimestampMixin):
    __tablename__ = "evidence_packet"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    zip_url: Mapped[str | None] = mapped_column(String(512))
    sha256: Mapped[str | None] = mapped_column(String(128))
    created_by: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("user_account.id", ondelete="SET NULL"), nullable=True
    )

    district: Mapped["District"] = relationship()
    creator: Mapped["UserAccount | None"] = relationship()
    items: Mapped[list["EvidenceItem"]] = relationship(
        back_populates="packet", cascade="all, delete-orphan"
    )


class EvidenceItem(Base, TimestampMixin):
    __tablename__ = "evidence_item"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    packet_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("evidence_packet.id", ondelete="SET NULL"), nullable=True
    )
    exception_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("exception_record.id", ondelete="SET NULL"), nullable=True
    )
    kind: Mapped[EvidenceKindEnum] = mapped_column(EvidenceKind, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    uri: Mapped[str] = mapped_column(String(512), nullable=False)

    district: Mapped["District"] = relationship()
    packet: Mapped["EvidencePacket | None"] = relationship(back_populates="items")
    exception: Mapped["ExceptionRecord | None"] = relationship()


class ExceptionMemo(Base, TimestampMixin):
    __tablename__ = "exception_memo"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    exception_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("exception_record.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(64), nullable=False, default="system")

    district: Mapped["District"] = relationship()
    exception: Mapped["ExceptionRecord"] = relationship()


class ReadinessScore(Base, TimestampMixin):
    __tablename__ = "readiness_score"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    school_id: Mapped[UUID | None] = mapped_column(
        GUID(), ForeignKey("school.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    district: Mapped["District"] = relationship()
    school: Mapped["School | None"] = relationship()


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4, nullable=False)
    district_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("district.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(GUID(), ForeignKey("user_account.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    entity_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    district: Mapped["District"] = relationship()
    user: Mapped["UserAccount | None"] = relationship()
