"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2024051401"
down_revision = None
branch_labels = None
depends_on = None


rule_run_status = sa.Enum(
    "pending",
    "running",
    "success",
    "failed",
    name="rule_run_status",
    native_enum=False,
)

rule_result_status = sa.Enum(
    "open",
    "resolved",
    "deferred",
    "accepted",
    name="rule_result_status",
    native_enum=False,
)

rule_severity = sa.Enum(
    "error",
    "warning",
    "info",
    name="rule_severity",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "district",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("nces_id", sa.String(length=32), nullable=True, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "school",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nces_id", sa.String(length=32), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_school_district_id", "school", ["district_id"])

    op.create_table(
        "student",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sis_id", sa.String(length=64), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("ell_status", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("idea_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enrollment_status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("enrollment_start", sa.Date(), nullable=True),
        sa.Column("enrollment_end", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["school.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_student_district_school", "student", ["district_id", "school_id"])
    op.create_index("ix_student_sis", "student", ["district_id", "sis_id"], unique=True)

    op.create_table(
        "rule_version",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("severity", rule_severity, nullable=False, server_default="error"),
        sa.Column("applies_to", sa.String(length=64), nullable=False),
        sa.Column("dsl", sa.JSON(), nullable=False),
        sa.Column("remediation", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_rule_version_code", "rule_version", ["code"])

    op.create_table(
        "rule_run",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("initiated_by", sa.String(length=255), nullable=True),
        sa.Column("status", rule_run_status, nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scope", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_version_id"], ["rule_version.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_rule_run_district", "rule_run", ["district_id"])

    op.create_table(
        "rule_result",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("rule_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", rule_severity, nullable=False, server_default="error"),
        sa.Column("status", rule_result_status, nullable=False, server_default="open"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_run_id"], ["rule_run.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["school.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_rule_result_district", "rule_result", ["district_id", "severity", "status"])



def downgrade() -> None:
    op.drop_index("ix_rule_result_district", table_name="rule_result")
    op.drop_table("rule_result")
    op.drop_index("ix_rule_run_district", table_name="rule_run")
    op.drop_table("rule_run")
    op.drop_index("ix_rule_version_code", table_name="rule_version")
    op.drop_table("rule_version")
    op.drop_index("ix_student_sis", table_name="student")
    op.drop_index("ix_student_district_school", table_name="student")
    op.drop_table("student")
    op.drop_index("ix_school_district_id", table_name="school")
    op.drop_table("school")
    op.drop_table("district")
    rule_result_status.drop(op.get_bind(), checkfirst=True)
    rule_run_status.drop(op.get_bind(), checkfirst=True)
    rule_severity.drop(op.get_bind(), checkfirst=True)
