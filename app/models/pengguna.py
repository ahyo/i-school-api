import uuid
from sqlalchemy import String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from app.db.base import Base


class PeranPengguna(PyEnum):
    admin_sekolah = "admin_sekolah"
    guru = "guru"
    operator = "operator"
    keuangan = "keuangan"


class Pengguna(Base):
    __tablename__ = "pengguna"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nama_lengkap: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    email_terverifikasi: Mapped[bool] = mapped_column(Boolean, default=False)
    kata_sandi_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    peran: Mapped[PeranPengguna] = mapped_column(Enum(PeranPengguna), nullable=False)
    sekolah_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="SET NULL")
    )
    status_aktif: Mapped[bool] = mapped_column(Boolean, default=True)

    sekolah = relationship("Sekolah", back_populates="pengguna")
    guru = relationship("Guru", back_populates="pengguna", uselist=False)
    konten_dibuat = relationship("WebsiteKonten", back_populates="penulis")
