import uuid
from datetime import date, datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.referensi import JenisKelamin


class StatusPendaftaran(PyEnum):
    menunggu = "menunggu"
    diproses = "diproses"
    diterima = "diterima"
    ditolak = "ditolak"


class PendaftaranSiswa(Base):
    __tablename__ = "pendaftaran_siswa"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    nama_lengkap: Mapped[str] = mapped_column(String(150), nullable=False)
    nama_panggilan: Mapped[str | None] = mapped_column(String(50))
    jenis_kelamin: Mapped[JenisKelamin] = mapped_column(
        Enum(JenisKelamin, native_enum=False)
    )
    tempat_lahir: Mapped[str | None] = mapped_column(String(100))
    tanggal_lahir: Mapped[date | None] = mapped_column(Date)
    agama: Mapped[str | None] = mapped_column(String(50))
    alamat: Mapped[str | None] = mapped_column(String(255))
    asal_sekolah: Mapped[str | None] = mapped_column(String(150))
    kelas_tujuan: Mapped[str | None] = mapped_column(String(100))
    nomor_telepon: Mapped[str | None] = mapped_column(String(25))
    email: Mapped[str | None] = mapped_column(String(150))
    nama_ayah: Mapped[str | None] = mapped_column(String(150))
    nama_ibu: Mapped[str | None] = mapped_column(String(150))
    nomor_hp_wali: Mapped[str | None] = mapped_column(String(25))
    catatan: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[StatusPendaftaran] = mapped_column(
        Enum(StatusPendaftaran, native_enum=False),
        default=StatusPendaftaran.menunggu,
        nullable=False,
    )
    catatan_admin: Mapped[str | None] = mapped_column(String(500))
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

    sekolah = relationship("Sekolah", back_populates="pendaftaran_siswa")
