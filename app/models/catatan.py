import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import (
    String,
    Enum,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class KategoriCatatan(PyEnum):
    perilaku = "perilaku"
    akademik = "akademik"
    kehadiran = "kehadiran"
    lainnya = "lainnya"


class CatatanSiswa(Base):
    __tablename__ = "catatan_siswa"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    pencatat_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("pengguna.id", ondelete="SET NULL"), nullable=True
    )
    kategori: Mapped[KategoriCatatan] = mapped_column(
        Enum(KategoriCatatan, native_enum=False), nullable=False, default=KategoriCatatan.lainnya
    )
    judul: Mapped[str | None] = mapped_column(String(150))
    isi: Mapped[str] = mapped_column(Text, nullable=False)
    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    siswa = relationship("Siswa", back_populates="catatan")
    pencatat = relationship("Pengguna", back_populates="catatan_dibuat")
    sekolah = relationship("Sekolah", back_populates="catatan_siswa")
