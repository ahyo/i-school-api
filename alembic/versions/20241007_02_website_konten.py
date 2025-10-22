"""Website konten module

Revision ID: 20241007_02
Revises: 20241007_01
Create Date: 2024-10-07 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20241007_02"
down_revision = "20241007_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    jenis_konten = sa.Enum(
        "berita",
        "kegiatan",
        "pengumuman",
        "prestasi",
        "lainnya",
        name="jeniskonten",
    )
    status_konten = sa.Enum(
        "draft",
        "terbit",
        "arsip",
        name="statuskonten",
    )
    jenis_konten.create(op.get_bind(), checkfirst=True)
    status_konten.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "website_konten",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("penulis_id", sa.String(), nullable=True),
        sa.Column("judul", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("jenis", jenis_konten, nullable=False),
        sa.Column("status", status_konten, nullable=False, server_default=sa.text("'draft'")),
        sa.Column("ringkasan", sa.String(length=500), nullable=True),
        sa.Column("isi", sa.Text(), nullable=False),
        sa.Column("banner_url", sa.String(length=255), nullable=True),
        sa.Column("tag_meta", sa.String(length=255), nullable=True),
        sa.Column("tanggal_terbit", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diperbarui_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["penulis_id"],
            ["pengguna.id"],
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "sekolah_id",
            "slug",
            name="uq_website_konten_sekolah_slug",
        ),
    )
    op.create_index(
        "ix_website_konten_slug",
        "website_konten",
        ["slug"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_website_konten_slug", table_name="website_konten")
    op.drop_table("website_konten")
    sa.Enum(name="statuskonten").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="jeniskonten").drop(op.get_bind(), checkfirst=True)
