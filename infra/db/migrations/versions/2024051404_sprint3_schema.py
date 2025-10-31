"""Sprint 3 SSO and audit log additions"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2024051404"
down_revision = "2024051403"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_account", sa.Column("sso_provider", sa.String(length=64), nullable=True))
    op.add_column("user_account", sa.Column("sso_subject", sa.String(length=255), nullable=True))
    op.add_column("user_account", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint("uq_user_sso", "user_account", ["sso_provider", "sso_subject"])

    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=128), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user_account.id"], ondelete="SET NULL"),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_constraint("uq_user_sso", "user_account", type_="unique")
    op.drop_column("user_account", "last_login_at")
    op.drop_column("user_account", "sso_subject")
    op.drop_column("user_account", "sso_provider")
