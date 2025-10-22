import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Enum, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class KelompokMataPelajaran(PyEnum):
    umum = "umum"
    keahlian = "keahlian"
    muatan_lokal = "muatan_lokal"
    tambahan = "tambahan"


class MataPelajaran(Base):
    __tablename__ = "mata_pelajaran"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    kode_mapel: Mapped[str | None] = mapped_column(String(20))
    nama_mapel: Mapped[str] = mapped_column(String(150), nullable=False)
    kelompok: Mapped[KelompokMataPelajaran] = mapped_column(
        Enum(KelompokMataPelajaran), nullable=False, default=KelompokMataPelajaran.umum
    )
    tingkat_minimal: Mapped[int | None] = mapped_column(Integer)
    tingkat_maksimal: Mapped[int | None] = mapped_column(Integer)
    status_aktif: Mapped[bool] = mapped_column(Boolean, default=True)

    sekolah = relationship("Sekolah", back_populates="mata_pelajaran")
    relasi_guru = relationship(
        "GuruMataPelajaran", back_populates="mata_pelajaran", cascade="all, delete-orphan"
    )
    nilai = relationship("Nilai", back_populates="mata_pelajaran")
    absensi = relationship("AbsensiSiswa", back_populates="mata_pelajaran")
