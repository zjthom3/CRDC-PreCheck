"""Sprint 2 schema additions"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2024051403"
down_revision = "2024051402"
branch_labels = None
depends_on = None

exception_status = sa.Enum("open", "in_review", "resolved", "won't_fix", name="exception_status", native_enum=False)
evidence_kind = sa.Enum("csv", "screenshot", "policy", "export", name="evidence_kind", native_enum=False)


def upgrade() -> None:
    exception_status.create(op.get_bind(), checkfirst=True)
    evidence_kind.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "exception_record",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", exception_status, nullable=False, server_default="open"),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("approval_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_result_id"], ["rule_result.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["user_account.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approval_user_id"], ["user_account.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "evidence_packet",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("zip_url", sa.String(length=512), nullable=True),
        sa.Column("sha256", sa.String(length=128), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["user_account.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "evidence_item",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("packet_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("exception_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("kind", evidence_kind, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("uri", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["packet_id"], ["evidence_packet.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["exception_id"], ["exception_record.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "exception_memo",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exception_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body_md", sa.Text(), nullable=False),
        sa.Column("generated_by", sa.String(length=64), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exception_id"], ["exception_record.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "readiness_score",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["school.id"], ondelete="SET NULL"),
    )


def downgrade() -> None:
    op.drop_table("readiness_score")
    op.drop_table("exception_memo")
    op.drop_table("evidence_item")
    op.drop_table("evidence_packet")
    op.drop_table("exception_record")

    evidence_kind.drop(op.get_bind(), checkfirst=True)
    exception_status.drop(op.get_bind(), checkfirst=True)
