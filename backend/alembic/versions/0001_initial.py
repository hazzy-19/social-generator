"""initial - create social_generations table

Revision ID: 0001
Revises:
Create Date: 2026-08-29

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    platform_type = postgresql.ENUM("instagram", "linkedin", "x", "facebook", name="platform_type")
    generation_status = postgresql.ENUM("draft", "ready", "saved", name="generation_status")
    platform_type.create(op.get_bind(), checkfirst=True)
    generation_status.create(op.get_bind(), checkfirst=True)

    platform_enum = postgresql.ENUM(
        "instagram", "linkedin", "x", "facebook", name="platform_type", create_type=False
    )
    status_enum = postgresql.ENUM(
        "draft", "ready", "saved", name="generation_status", create_type=False
    )

    op.create_table(
        "social_generations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_content", sa.Text(), nullable=False),
        sa.Column("platform", platform_enum, nullable=False),
        sa.Column("image_query", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("image_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("hashtags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("hashtags_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("caption_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("char_limit", sa.Integer(), nullable=False),
        sa.Column("char_count", sa.Integer(), nullable=True),
        sa.Column("status", status_enum, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_social_generations_status", "social_generations", ["status"])
    op.create_index("idx_social_generations_platform", "social_generations", ["platform"])
    op.create_index("idx_social_generations_created_at", "social_generations", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_social_generations_created_at", table_name="social_generations")
    op.drop_index("idx_social_generations_platform", table_name="social_generations")
    op.drop_index("idx_social_generations_status", table_name="social_generations")
    op.drop_table("social_generations")
    postgresql.ENUM(name="generation_status").drop(op.get_bind())
    postgresql.ENUM(name="platform_type").drop(op.get_bind())
