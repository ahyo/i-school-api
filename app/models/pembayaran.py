import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    String,
    Enum,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class JenisPembayaran(PyEnum):
    spp = "spp"
    daftar_ulang = "daftar_ulang"
    kegiatan = "kegiatan"
    seragam = "seragam"
    lainnya = "lainnya"


class StatusPembayaran(PyEnum):
    menunggu = "menunggu"
    lunas = "lunas"
    menunggak = "menunggak"


class StatusTagihan(PyEnum):
    belum_dibayar = "belum_dibayar"
    sebagian = "sebagian"
    lunas = "lunas"
    menunggak = "menunggak"


class Tagihan(Base):
    __tablename__ = "tagihan"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    jenis_tagihan: Mapped[JenisPembayaran] = mapped_column(
        Enum(JenisPembayaran), nullable=False
    )
    nama_tagihan: Mapped[str] = mapped_column(String(150), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text)
    periode_bulan: Mapped[int | None] = mapped_column(Integer)
    periode_tahun: Mapped[int | None] = mapped_column(Integer)
    tanggal_tagihan: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    tanggal_jatuh_tempo: Mapped[date | None] = mapped_column(Date)
    jumlah_tagihan: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    jumlah_terbayar: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    status_tagihan: Mapped[StatusTagihan] = mapped_column(
        Enum(StatusTagihan), nullable=False, default=StatusTagihan.belum_dibayar
    )
    tanggal_lunas: Mapped[date | None] = mapped_column(Date)
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

    sekolah = relationship("Sekolah", back_populates="tagihan")
    siswa = relationship("Siswa", back_populates="tagihan")
    pembayaran = relationship(
        "Pembayaran", back_populates="tagihan", cascade="all, delete-orphan"
    )


class Pembayaran(Base):
    __tablename__ = "pembayaran"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    tagihan_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("tagihan.id", ondelete="SET NULL")
    )
    jenis_pembayaran: Mapped[JenisPembayaran] = mapped_column(
        Enum(JenisPembayaran), nullable=False
    )
    deskripsi: Mapped[str | None] = mapped_column(Text)
    periode: Mapped[str | None] = mapped_column(String(20))
    jumlah: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tanggal_jatuh_tempo: Mapped[date | None] = mapped_column(Date)
    tanggal_bayar: Mapped[date | None] = mapped_column(Date)
    status_pembayaran: Mapped[StatusPembayaran] = mapped_column(
        Enum(StatusPembayaran), nullable=False, default=StatusPembayaran.menunggu
    )
    metode_pembayaran: Mapped[str | None] = mapped_column(String(50))
    bukti_pembayaran_url: Mapped[str | None] = mapped_column(String(255))
    keterangan: Mapped[str | None] = mapped_column(Text)
    dicatat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    sekolah = relationship("Sekolah", back_populates="pembayaran")
    siswa = relationship("Siswa", back_populates="pembayaran")
    tagihan = relationship("Tagihan", back_populates="pembayaran")
