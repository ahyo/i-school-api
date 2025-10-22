import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import (
    String,
    Enum,
    Boolean,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class JenjangSekolah(PyEnum):
    sd = "SD"
    smp = "SMP"
    sma = "SMA"
    smk = "SMK"


class StatusSekolah(PyEnum):
    negeri = "negeri"
    swasta = "swasta"


class Sekolah(Base):
    __tablename__ = "sekolah"
    __table_args__ = (
        UniqueConstraint(
            "npsn",
            name="uq_sekolah_npsn",
        ),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nama_sekolah: Mapped[str] = mapped_column(String(200), nullable=False)
    npsn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    jenjang: Mapped[JenjangSekolah] = mapped_column(
        Enum(JenjangSekolah), nullable=False
    )
    status: Mapped[StatusSekolah] = mapped_column(
        Enum(StatusSekolah), nullable=False, default=StatusSekolah.negeri
    )
    alamat_jalan: Mapped[str | None] = mapped_column(String(255))
    kelurahan: Mapped[str | None] = mapped_column(String(100))
    kecamatan: Mapped[str | None] = mapped_column(String(100))
    kota_kabupaten: Mapped[str | None] = mapped_column(String(100))
    provinsi: Mapped[str | None] = mapped_column(String(100))
    kode_pos: Mapped[str | None] = mapped_column(String(10))
    nomor_telepon: Mapped[str | None] = mapped_column(String(25))
    email_resmi: Mapped[str | None] = mapped_column(String(150))
    website: Mapped[str | None] = mapped_column(String(150))
    kepala_sekolah: Mapped[str | None] = mapped_column(String(150))
    tanggal_berdiri: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deskripsi: Mapped[str | None] = mapped_column(String(500))
    status_verifikasi: Mapped[bool] = mapped_column(Boolean, default=False)
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

    pengguna = relationship("Pengguna", back_populates="sekolah")
    guru = relationship("Guru", back_populates="sekolah")
    siswa = relationship("Siswa", back_populates="sekolah")
    mata_pelajaran = relationship("MataPelajaran", back_populates="sekolah")
    kelas = relationship("Kelas", back_populates="sekolah")
    tahun_ajaran = relationship("TahunAjaran", back_populates="sekolah")
    pembayaran = relationship("Pembayaran", back_populates="sekolah")
    absensi = relationship("AbsensiSiswa", back_populates="sekolah")
    nilai = relationship("Nilai", back_populates="sekolah")
    tagihan = relationship("Tagihan", back_populates="sekolah")
    konten_website = relationship("WebsiteKonten", back_populates="sekolah")
