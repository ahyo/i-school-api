import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class JenisKonten(PyEnum):
    berita = "berita"
    kegiatan = "kegiatan"
    pengumuman = "pengumuman"
    prestasi = "prestasi"
    lainnya = "lainnya"


class StatusKonten(PyEnum):
    draft = "draft"
    terbit = "terbit"
    arsip = "arsip"


class WebsiteKonten(Base):
    __tablename__ = "website_konten"
    __table_args__ = (
        UniqueConstraint(
            "sekolah_id",
            "slug",
            name="uq_website_konten_sekolah_slug",
        ),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    penulis_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("pengguna.id", ondelete="SET NULL")
    )
    judul: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    jenis: Mapped[JenisKonten] = mapped_column(Enum(JenisKonten), nullable=False)
    status: Mapped[StatusKonten] = mapped_column(
        Enum(StatusKonten), nullable=False, default=StatusKonten.draft
    )
    ringkasan: Mapped[str | None] = mapped_column(String(500))
    isi: Mapped[str] = mapped_column(Text, nullable=False)
    banner_url: Mapped[str | None] = mapped_column(String(255))
    tag_meta: Mapped[str | None] = mapped_column(String(255))
    tanggal_terbit: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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

    sekolah = relationship("Sekolah", back_populates="konten_website")
    penulis = relationship("Pengguna", back_populates="konten_dibuat")
