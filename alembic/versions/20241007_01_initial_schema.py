"""Initial database schema

Revision ID: 20241007_01
Revises:
Create Date: 2024-10-07 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


def create_enum_if_not_exists(name: str, values: tuple[str, ...]) -> None:
    values_sql = ", ".join(f"'{value}'" for value in values)
    op.execute(
        sa.text(
            "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '"
            + name
            + "') THEN CREATE TYPE "
            + name
            + " AS ENUM ("
            + values_sql
            + "); END IF; END $$;"
        )
    )


revision = "20241007_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    for enum_name in [
        "peranpengguna",
        "statusguru",
        "jeniskelamin",
        "jenjangsekolah",
        "statussekolah",
        "kelompokmatapelajaran",
        "statussiswa",
        "statuskeanggotaan",
        "semester",
        "tipepenilaian",
        "statuskehadiran",
        "statuskenaikan",
        "jenispembayaran",
        "statuspembayaran",
        "statustagihan",
    ]:
        op.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))

    peran_pengguna = sa.Enum(
        "admin_sekolah",
        "guru",
        "operator",
        "keuangan",
        name="peranpengguna",
        create_type=False,
    )
    status_guru = sa.Enum(
        "aktif", "tidak_aktif", "cuti", name="statusguru", create_type=False
    )
    jenis_kelamin = sa.Enum(
        "laki_laki", "perempuan", name="jeniskelamin", create_type=False
    )
    jenjang_sekolah = sa.Enum(
        "SD", "SMP", "SMA", "SMK", name="jenjangsekolah", create_type=False
    )
    status_sekolah = sa.Enum(
        "negeri", "swasta", name="statussekolah", create_type=False
    )
    kelompok_mapel = sa.Enum(
        "umum", "keahlian", "muatan_lokal", "tambahan", name="kelompokmatapelajaran"
    )
    kelompok_mapel.create_type = False
    status_siswa = sa.Enum(
        "aktif", "lulus", "mutasi", "keluar", name="statussiswa", create_type=False
    )
    status_keanggotaan = sa.Enum(
        "aktif", "pindah", "naik", "tinggal_kelas", name="statuskeanggotaan"
    )
    status_keanggotaan.create_type = False
    semester_enum = sa.Enum(
        "ganjil", "genap", name="semester", create_type=False
    )
    tipe_penilaian = sa.Enum(
        "pengetahuan", "keterampilan", "sikap", "uts", "uas", name="tipepenilaian"
    )
    tipe_penilaian.create_type = False
    status_kehadiran = sa.Enum(
        "hadir", "sakit", "izin", "alfa", "terlambat", name="statuskehadiran"
    )
    status_kehadiran.create_type = False
    status_kenaikan = sa.Enum(
        "naik", "tinggal", "mutasi_keluar", name="statuskenaikan", create_type=False
    )
    jenis_pembayaran = sa.Enum(
        "spp",
        "daftar_ulang",
        "kegiatan",
        "seragam",
        "lainnya",
        name="jenispembayaran",
        create_type=False,
    )
    status_pembayaran = sa.Enum(
        "menunggu", "lunas", "menunggak", name="statuspembayaran", create_type=False
    )
    status_tagihan = sa.Enum(
        "belum_dibayar", "sebagian", "lunas", "menunggak", name="statustagihan", create_type=False
    )

    create_enum_if_not_exists("peranpengguna", peran_pengguna.enums)
    create_enum_if_not_exists("statusguru", status_guru.enums)
    create_enum_if_not_exists("jeniskelamin", jenis_kelamin.enums)
    create_enum_if_not_exists("jenjangsekolah", jenjang_sekolah.enums)
    create_enum_if_not_exists("statussekolah", status_sekolah.enums)
    create_enum_if_not_exists("kelompokmatapelajaran", kelompok_mapel.enums)
    create_enum_if_not_exists("statussiswa", status_siswa.enums)
    create_enum_if_not_exists("statuskeanggotaan", status_keanggotaan.enums)
    create_enum_if_not_exists("semester", semester_enum.enums)
    create_enum_if_not_exists("tipepenilaian", tipe_penilaian.enums)
    create_enum_if_not_exists("statuskehadiran", status_kehadiran.enums)
    create_enum_if_not_exists("statuskenaikan", status_kenaikan.enums)
    create_enum_if_not_exists("jenispembayaran", jenis_pembayaran.enums)
    create_enum_if_not_exists("statuspembayaran", status_pembayaran.enums)
    create_enum_if_not_exists("statustagihan", status_tagihan.enums)

    op.create_table(
        "sekolah",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("nama_sekolah", sa.String(length=200), nullable=False),
        sa.Column("npsn", sa.String(length=20)),
        sa.Column("jenjang", jenjang_sekolah, nullable=False),
        sa.Column("status", status_sekolah, nullable=False),
        sa.Column("alamat_jalan", sa.String(length=255)),
        sa.Column("kelurahan", sa.String(length=100)),
        sa.Column("kecamatan", sa.String(length=100)),
        sa.Column("kota_kabupaten", sa.String(length=100)),
        sa.Column("provinsi", sa.String(length=100)),
        sa.Column("kode_pos", sa.String(length=10)),
        sa.Column("nomor_telepon", sa.String(length=25)),
        sa.Column("email_resmi", sa.String(length=150)),
        sa.Column("website", sa.String(length=150)),
        sa.Column("kepala_sekolah", sa.String(length=150)),
        sa.Column("tanggal_berdiri", sa.DateTime(timezone=True)),
        sa.Column("deskripsi", sa.String(length=500)),
        sa.Column(
            "status_verifikasi",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diperbarui_pada", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("npsn", name="uq_sekolah_npsn"),
    )

    op.create_table(
        "pengguna",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("nama_lengkap", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column(
            "email_terverifikasi",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("kata_sandi_hash", sa.String(length=255), nullable=False),
        sa.Column("peran", peran_pengguna, nullable=False),
        sa.Column(
            "sekolah_id", sa.String(), sa.ForeignKey("sekolah.id", ondelete="SET NULL")
        ),
        sa.Column(
            "status_aktif", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.UniqueConstraint("email", name="uq_pengguna_email"),
    )
    op.create_index("ix_pengguna_email", "pengguna", ["email"])

    op.create_table(
        "token_verifikasi_email",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("pengguna_id", sa.String(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("kedaluwarsa", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "digunakan", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.ForeignKeyConstraint(
            ["pengguna_id"],
            ["pengguna.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token", name="uq_token_verifikasi_token"),
    )
    op.create_index(
        "ix_token_verifikasi_email_pengguna_id",
        "token_verifikasi_email",
        ["pengguna_id"],
    )

    op.create_table(
        "guru",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("pengguna_id", sa.String(), nullable=False, unique=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("nuptk", sa.String(length=20)),
        sa.Column("nip", sa.String(length=20)),
        sa.Column("tempat_lahir", sa.String(length=100)),
        sa.Column("tanggal_lahir", sa.Date()),
        sa.Column("jenis_kelamin", jenis_kelamin),
        sa.Column("nomor_telepon", sa.String(length=25)),
        sa.Column("alamat", sa.String(length=255)),
        sa.Column("mata_pelajaran_utama", sa.String(length=100)),
        sa.Column(
            "status_guru",
            status_guru,
            nullable=False,
            server_default=sa.text("'aktif'"),
        ),
        sa.ForeignKeyConstraint(
            ["pengguna_id"],
            ["pengguna.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "mata_pelajaran",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("kode_mapel", sa.String(length=20)),
        sa.Column("nama_mapel", sa.String(length=150), nullable=False),
        sa.Column(
            "kelompok", kelompok_mapel, nullable=False, server_default=sa.text("'umum'")
        ),
        sa.Column("tingkat_minimal", sa.Integer()),
        sa.Column("tingkat_maksimal", sa.Integer()),
        sa.Column(
            "status_aktif", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "tahun_ajaran",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("nama_tahun", sa.String(length=20), nullable=False),
        sa.Column("tanggal_mulai", sa.Date(), nullable=False),
        sa.Column("tanggal_selesai", sa.Date(), nullable=False),
        sa.Column("semester_awal", semester_enum, nullable=False),
        sa.Column(
            "aktif", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "siswa",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("nisn", sa.String(length=20)),
        sa.Column("nis", sa.String(length=20)),
        sa.Column("nama_lengkap", sa.String(length=150), nullable=False),
        sa.Column("nama_panggilan", sa.String(length=50)),
        sa.Column("jenis_kelamin", jenis_kelamin, nullable=False),
        sa.Column("tempat_lahir", sa.String(length=100)),
        sa.Column("tanggal_lahir", sa.Date()),
        sa.Column("agama", sa.String(length=50)),
        sa.Column("alamat", sa.String(length=255)),
        sa.Column("nomor_telepon", sa.String(length=25)),
        sa.Column("nama_ayah", sa.String(length=150)),
        sa.Column("nama_ibu", sa.String(length=150)),
        sa.Column("wali_murid", sa.String(length=150)),
        sa.Column(
            "status_siswa",
            status_siswa,
            nullable=False,
            server_default=sa.text("'aktif'"),
        ),
        sa.Column("tanggal_diterima", sa.Date()),
        sa.Column("catatan", sa.String(length=500)),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diperbarui_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("nisn", name="uq_siswa_nisn"),
    )

    op.create_table(
        "kelas",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("tahun_ajaran_id", sa.String(), nullable=False),
        sa.Column("nama_kelas", sa.String(length=100), nullable=False),
        sa.Column("tingkat", sa.Integer(), nullable=False),
        sa.Column("rombel", sa.String(length=50)),
        sa.Column("jurusan", sa.String(length=100)),
        sa.Column("wali_kelas_id", sa.String()),
        sa.Column("kapasitas", sa.Integer()),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tahun_ajaran_id"],
            ["tahun_ajaran.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["wali_kelas_id"],
            ["guru.id"],
            ondelete="SET NULL",
        ),
    )

    op.create_table(
        "siswa_kelas",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("kelas_id", sa.String(), nullable=False),
        sa.Column(
            "status_keanggotaan",
            status_keanggotaan,
            nullable=False,
            server_default=sa.text("'aktif'"),
        ),
        sa.Column("tanggal_masuk", sa.Date()),
        sa.Column("tanggal_keluar", sa.Date()),
        sa.ForeignKeyConstraint(
            ["siswa_id"],
            ["siswa.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kelas_id"],
            ["kelas.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "guru_mata_pelajaran",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("guru_id", sa.String(), nullable=False),
        sa.Column("mata_pelajaran_id", sa.String(), nullable=False),
        sa.Column("kelas_id", sa.String()),
        sa.ForeignKeyConstraint(
            ["guru_id"],
            ["guru.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mata_pelajaran_id"],
            ["mata_pelajaran.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kelas_id"],
            ["kelas.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "tagihan",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("jenis_tagihan", jenis_pembayaran, nullable=False),
        sa.Column("nama_tagihan", sa.String(length=150), nullable=False),
        sa.Column("deskripsi", sa.Text()),
        sa.Column("periode_bulan", sa.Integer()),
        sa.Column("periode_tahun", sa.Integer()),
        sa.Column(
            "tanggal_tagihan",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("tanggal_jatuh_tempo", sa.Date()),
        sa.Column("jumlah_tagihan", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "jumlah_terbayar",
            sa.Numeric(14, 2),
            nullable=False,
            server_default=sa.text("0.00"),
        ),
        sa.Column(
            "status_tagihan",
            status_tagihan,
            nullable=False,
            server_default=sa.text("'belum_dibayar'"),
        ),
        sa.Column("tanggal_lunas", sa.Date()),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diperbarui_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["siswa_id"],
            ["siswa.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "nilai",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("kelas_id", sa.String()),
        sa.Column("mata_pelajaran_id", sa.String(), nullable=False),
        sa.Column("guru_id", sa.String()),
        sa.Column("tahun_ajaran_id", sa.String(), nullable=False),
        sa.Column("semester", semester_enum, nullable=False),
        sa.Column("tipe_penilaian", tipe_penilaian, nullable=False),
        sa.Column("nilai_angka", sa.Numeric(5, 2)),
        sa.Column("nilai_huruf", sa.String(length=5)),
        sa.Column("deskripsi", sa.Text()),
        sa.Column("tanggal_penilaian", sa.Date()),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["siswa_id"],
            ["siswa.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kelas_id"],
            ["kelas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["mata_pelajaran_id"],
            ["mata_pelajaran.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["guru_id"],
            ["guru.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["tahun_ajaran_id"],
            ["tahun_ajaran.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "absensi_siswa",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("kelas_id", sa.String()),
        sa.Column("mata_pelajaran_id", sa.String()),
        sa.Column("tanggal", sa.Date(), nullable=False),
        sa.Column("status_kehadiran", status_kehadiran, nullable=False),
        sa.Column("keterangan", sa.Text()),
        sa.Column("dicatat_oleh_id", sa.String()),
        sa.Column("dibuat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["siswa_id"],
            ["siswa.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kelas_id"],
            ["kelas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["mata_pelajaran_id"],
            ["mata_pelajaran.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["dicatat_oleh_id"],
            ["guru.id"],
            ondelete="SET NULL",
        ),
    )

    op.create_table(
        "kenaikan_kelas",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("kelas_asal_id", sa.String()),
        sa.Column("kelas_tujuan_id", sa.String()),
        sa.Column("tahun_ajaran_asal_id", sa.String()),
        sa.Column("tahun_ajaran_tujuan_id", sa.String(), nullable=False),
        sa.Column("status_kenaikan", status_kenaikan, nullable=False),
        sa.Column("tanggal_keputusan", sa.Date()),
        sa.Column("catatan", sa.Text()),
        sa.ForeignKeyConstraint(
            ["siswa_id"],
            ["siswa.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kelas_asal_id"],
            ["kelas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["kelas_tujuan_id"],
            ["kelas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["tahun_ajaran_asal_id"],
            ["tahun_ajaran.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["tahun_ajaran_tujuan_id"],
            ["tahun_ajaran.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "pembayaran",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("sekolah_id", sa.String(), nullable=False),
        sa.Column("siswa_id", sa.String(), nullable=False),
        sa.Column("tagihan_id", sa.String()),
        sa.Column("jenis_pembayaran", jenis_pembayaran, nullable=False),
        sa.Column("deskripsi", sa.Text()),
        sa.Column("periode", sa.String(length=20)),
        sa.Column("jumlah", sa.Numeric(14, 2), nullable=False),
        sa.Column("tanggal_jatuh_tempo", sa.Date()),
        sa.Column("tanggal_bayar", sa.Date()),
        sa.Column(
            "status_pembayaran",
            status_pembayaran,
            nullable=False,
            server_default=sa.text("'menunggu'"),
        ),
        sa.Column("metode_pembayaran", sa.String(length=50)),
        sa.Column("bukti_pembayaran_url", sa.String(length=255)),
        sa.Column("keterangan", sa.Text()),
        sa.Column("dicatat_pada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sekolah_id"],
            ["sekolah.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["siswa_id"],
            ["siswa.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tagihan_id"],
            ["tagihan.id"],
            ondelete="SET NULL",
        ),
    )


def downgrade() -> None:
    op.drop_table("pembayaran")
    op.drop_table("kenaikan_kelas")
    op.drop_table("absensi_siswa")
    op.drop_table("nilai")
    op.drop_table("tagihan")
    op.drop_table("guru_mata_pelajaran")
    op.drop_table("siswa_kelas")
    op.drop_table("kelas")
    op.drop_table("siswa")
    op.drop_table("tahun_ajaran")
    op.drop_table("mata_pelajaran")
    op.drop_table("guru")
    op.drop_table("token_verifikasi_email")
    op.drop_index("ix_pengguna_email", table_name="pengguna")
    op.drop_table("pengguna")
    op.drop_table("sekolah")

    sa.Enum(name="statustagihan").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statuspembayaran").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="jenispembayaran").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statuskenaikan").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statuskehadiran").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tipepenilaian").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="semester").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statuskeanggotaan").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statussiswa").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="kelompokmatapelajaran").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statussekolah").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="jenjangsekolah").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="jeniskelamin").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="statusguru").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="peranpengguna").drop(op.get_bind(), checkfirst=True)
