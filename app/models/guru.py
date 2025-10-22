import uuid
from datetime import date
from enum import Enum as PyEnum
from sqlalchemy import String, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.referensi import JenisKelamin


class StatusGuru(PyEnum):
    aktif = "aktif"
    tidak_aktif = "tidak_aktif"
    cuti = "cuti"


class Guru(Base):
    __tablename__ = "guru"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    pengguna_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("pengguna.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    nuptk: Mapped[str | None] = mapped_column(String(20))
    nip: Mapped[str | None] = mapped_column(String(20))
    tempat_lahir: Mapped[str | None] = mapped_column(String(100))
    tanggal_lahir: Mapped[date | None] = mapped_column(Date)
    jenis_kelamin: Mapped[JenisKelamin | None] = mapped_column(
        Enum(JenisKelamin), nullable=True
    )
    nomor_telepon: Mapped[str | None] = mapped_column(String(25))
    alamat: Mapped[str | None] = mapped_column(String(255))
    mata_pelajaran_utama: Mapped[str | None] = mapped_column(String(100))
    status_guru: Mapped[StatusGuru] = mapped_column(
        Enum(StatusGuru), nullable=False, default=StatusGuru.aktif
    )

    pengguna = relationship("Pengguna", back_populates="guru")
    sekolah = relationship("Sekolah", back_populates="guru")
    wali_kelas_dari = relationship("Kelas", back_populates="wali_kelas")
    mata_pelajaran_diampu = relationship(
        "GuruMataPelajaran", back_populates="guru", cascade="all, delete-orphan"
    )
    nilai_diinput = relationship("Nilai", back_populates="guru")
    absensi_dicatat = relationship("AbsensiSiswa", back_populates="dicatat_oleh")
