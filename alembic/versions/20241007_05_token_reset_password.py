"""Tambah tabel token reset password

Revision ID: 20241007_05
Revises: 20241007_04
Create Date: 2024-10-07 02:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20241007_05"
down_revision = "20241007_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "token_reset_password",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("pengguna_id", sa.String(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("kedaluwarsa", sa.DateTime(timezone=True), nullable=False),
        sa.Column("digunakan", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["pengguna_id"], ["pengguna.id"], ondelete="CASCADE"),
    )

    op.create_index(
        "ix_token_reset_password_pengguna",
        "token_reset_password",
        ["pengguna_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_token_reset_password_pengguna", table_name="token_reset_password")
    op.drop_table("token_reset_password")
