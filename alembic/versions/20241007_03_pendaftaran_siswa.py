"""Tambah tabel pendaftaran siswa

Revision ID: 20241007_03
Revises: 20241007_02
Create Date: 2024-10-07 01:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20241007_03"
down_revision = "20241007_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_kwargs = {"native_enum": False}
    jenis_kelamin = sa.Enum(
        "laki_laki",
        "perempuan",
        name="jeniskelamin",
        create_type=False,
        **enum_kwargs,
    )
    status_pendaftaran = sa.Enum(
        "menunggu",
        "diproses",
        "diterima",
        "ditolak",
        name="statuspendaftaran",
        **enum_kwargs,
    )

    op.create_table(
        "pendaftaran_siswa",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("nama_lengkap", sa.String(length=150), nullable=False),
        sa.Column("nama_panggilan", sa.String(length=50), nullable=True),
        sa.Column(
            "jenis_kelamin",
            jenis_kelamin,
            nullable=False,
        ),
        sa.Column("tempat_lahir", sa.String(length=100), nullable=True),
        sa.Column("tanggal_lahir", sa.Date(), nullable=True),
        sa.Column("agama", sa.String(length=50), nullable=True),
        sa.Column("alamat", sa.String(length=255), nullable=True),
        sa.Column("asal_sekolah", sa.String(length=150), nullable=True),
        sa.Column("kelas_tujuan", sa.String(length=100), nullable=True),
        sa.Column("nomor_telepon", sa.String(length=25), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("nama_ayah", sa.String(length=150), nullable=True),
        sa.Column("nama_ibu", sa.String(length=150), nullable=True),
        sa.Column("nomor_hp_wali", sa.String(length=25), nullable=True),
        sa.Column("catatan", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            status_pendaftaran,
            nullable=False,
            server_default=sa.text("'menunggu'"),
        ),
        sa.Column("catatan_admin", sa.String(length=500), nullable=True),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diperbarui_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_pendaftaran_siswa_sekolah",
        "pendaftaran_siswa",
        ["sekolah_id"],
        unique=False,
    )
    op.create_index(
        "ix_pendaftaran_siswa_status",
        "pendaftaran_siswa",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pendaftaran_siswa_status", table_name="pendaftaran_siswa")
    op.drop_index("ix_pendaftaran_siswa_sekolah", table_name="pendaftaran_siswa")
    op.drop_table("pendaftaran_siswa")
