"""Tambah tabel catatan siswa

Revision ID: 20241007_04
Revises: 20241007_03
Create Date: 2024-10-07 01:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20241007_04"
down_revision = "20241007_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_kwargs = {"native_enum": False}
    kategori_enum = sa.Enum(
        "perilaku",
        "akademik",
        "kehadiran",
        "lainnya",
        name="kategoricatatan",
        **enum_kwargs,
    )

    op.create_table(
        "catatan_siswa",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("pencatat_id", sa.String(), nullable=True),
        sa.Column("kategori", kategori_enum, nullable=False, server_default=sa.text("'lainnya'")),
        sa.Column("judul", sa.String(length=150), nullable=True),
        sa.Column("isi", sa.Text(), nullable=False),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sekolah_id"], ["sekolah.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["siswa_id"], ["siswa.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["pencatat_id"], ["pengguna.id"], ondelete="SET NULL"),
    )

    op.create_index(
        "ix_catatan_siswa_sekolah",
        "catatan_siswa",
        ["sekolah_id"],
        unique=False,
    )
    op.create_index(
        "ix_catatan_siswa_siswa",
        "catatan_siswa",
        ["siswa_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_catatan_siswa_siswa", table_name="catatan_siswa")
    op.drop_index("ix_catatan_siswa_sekolah", table_name="catatan_siswa")
    op.drop_table("catatan_siswa")
