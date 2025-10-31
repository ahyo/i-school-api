import uuid
from datetime import date, datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import (
    String,
    Date,
    Enum,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.referensi import JenisKelamin


class StatusSiswa(PyEnum):
    aktif = "aktif"
    lulus = "lulus"
    mutasi = "mutasi"
    keluar = "keluar"


class Siswa(Base):
    __tablename__ = "siswa"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    nisn: Mapped[str | None] = mapped_column(String(20), unique=True)
    nis: Mapped[str | None] = mapped_column(String(20))
    nama_lengkap: Mapped[str] = mapped_column(String(150), nullable=False)
    nama_panggilan: Mapped[str | None] = mapped_column(String(50))
    jenis_kelamin: Mapped[JenisKelamin] = mapped_column(
        Enum(JenisKelamin, native_enum=False)
    )
    tempat_lahir: Mapped[str | None] = mapped_column(String(100))
    tanggal_lahir: Mapped[date | None] = mapped_column(Date)
    agama: Mapped[str | None] = mapped_column(String(50))
    alamat: Mapped[str | None] = mapped_column(String(255))
    nomor_telepon: Mapped[str | None] = mapped_column(String(25))
    nama_ayah: Mapped[str | None] = mapped_column(String(150))
    nama_ibu: Mapped[str | None] = mapped_column(String(150))
    wali_murid: Mapped[str | None] = mapped_column(String(150))
    status_siswa: Mapped[StatusSiswa] = mapped_column(
        Enum(StatusSiswa, native_enum=False), nullable=False, default=StatusSiswa.aktif
    )
    tanggal_diterima: Mapped[date | None] = mapped_column(Date)
    catatan: Mapped[str | None] = mapped_column(String(500))
    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    diperbarui_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sekolah = relationship("Sekolah", back_populates="siswa")
    riwayat_kelas = relationship(
        "SiswaKelas", back_populates="siswa", cascade="all, delete-orphan"
    )
    nilai = relationship("Nilai", back_populates="siswa")
    absensi = relationship("AbsensiSiswa", back_populates="siswa")
    pembayaran = relationship("Pembayaran", back_populates="siswa")
    riwayat_kenaikan = relationship(
        "KenaikanKelas", back_populates="siswa", cascade="all, delete-orphan"
    )
    tagihan = relationship("Tagihan", back_populates="siswa")
    catatan = relationship(
        "CatatanSiswa", back_populates="siswa", cascade="all, delete-orphan"
    )
    kelas_siswa = relationship("SiswaKelas", back_populates="siswa")


class StatusKeanggotaanKelas(PyEnum):
    aktif = "aktif"
    pindah = "pindah"
    naik = "naik"
    tinggal_kelas = "tinggal_kelas"


class SiswaKelas(Base):
    __tablename__ = "siswa_kelas"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    kelas_id: Mapped[str] = mapped_column(
        String, ForeignKey("kelas.id", ondelete="CASCADE"), nullable=False
    )
    status_keanggotaan: Mapped[StatusKeanggotaanKelas] = mapped_column(
        Enum(StatusKeanggotaanKelas, native_enum=False),
        nullable=False,
        default=StatusKeanggotaanKelas.aktif,
    )
    tanggal_masuk: Mapped[date | None] = mapped_column(Date)
    tanggal_keluar: Mapped[date | None] = mapped_column(Date)

    siswa = relationship("Siswa", back_populates="riwayat_kelas")
    kelas = relationship("Kelas", back_populates="anggota")
