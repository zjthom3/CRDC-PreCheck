"""Sprint 1 schema additions"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2024051402"
down_revision = "2024051401"
branch_labels = None
depends_on = None

user_role = sa.Enum("admin", "data_engineer", "reviewer", "readonly", name="user_role", native_enum=False)
connector_status = sa.Enum("healthy", "degraded", "error", name="connector_status", native_enum=False)
auth_method = sa.Enum("oauth", "token", "csv_upload", name="auth_method", native_enum=False)
sync_status = sa.Enum("queued", "running", "success", "failed", name="sync_status", native_enum=False)
ingest_status = sa.Enum("pending", "success", "failed", name="ingest_status", native_enum=False)


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    connector_status.create(op.get_bind(), checkfirst=True)
    auth_method.create(op.get_bind(), checkfirst=True)
    sync_status.create(op.get_bind(), checkfirst=True)
    ingest_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "user_account",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="admin"),
        sa.Column("api_token", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("district_id", "email", name="uq_user_district_email"),
        sa.UniqueConstraint("api_token", name="uq_user_api_token"),
    )

    op.create_table(
        "source_system",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "connector",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_method", auth_method, nullable=False),
        sa.Column("status", connector_status, nullable=False, server_default="healthy"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_system_id"], ["source_system.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "sync_job",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("connector_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sync_status, nullable=False, server_default="queued"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connector_id"], ["connector.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "ingest_batch",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_system_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sync_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("table_name", sa.String(length=64), nullable=False),
        sa.Column("rows_ingested", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", ingest_status, nullable=False, server_default="pending"),
        sa.Column("source_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_system_id"], ["source_system.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sync_job_id"], ["sync_job.id"], ondelete="SET NULL"),
    )

    op.create_unique_constraint("uq_student_district_sis", "student", ["district_id", "sis_id"])


def downgrade() -> None:
    op.drop_constraint("uq_student_district_sis", "student", type_="unique")
    op.drop_table("ingest_batch")
    op.drop_table("sync_job")
    op.drop_table("connector")
    op.drop_table("source_system")
    op.drop_table("user_account")

    ingest_status.drop(op.get_bind(), checkfirst=True)
    sync_status.drop(op.get_bind(), checkfirst=True)
    auth_method.drop(op.get_bind(), checkfirst=True)
    connector_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
