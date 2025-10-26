"""Tambah tabel refresh token

Revision ID: 20241007_06
Revises: 20241007_05
Create Date: 2024-10-07 02:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20241007_06"
down_revision = "20241007_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("pengguna_id", sa.String(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("kedaluwarsa", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dicabut", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pengguna_id"], ["pengguna.id"], ondelete="CASCADE"),
    )

    op.create_index(
        "ix_refresh_token_pengguna",
        "refresh_token",
        ["pengguna_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_token_pengguna", table_name="refresh_token")
    op.drop_table("refresh_token")
