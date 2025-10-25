import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    String,
    Integer,
    Enum,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Semester(PyEnum):
    ganjil = "ganjil"
    genap = "genap"


class TahunAjaran(Base):
    __tablename__ = "tahun_ajaran"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    nama_tahun: Mapped[str] = mapped_column(String(20), nullable=False)
    tanggal_mulai: Mapped[date] = mapped_column(Date, nullable=False)
    tanggal_selesai: Mapped[date] = mapped_column(Date, nullable=False)
    semester_awal: Mapped[Semester] = mapped_column(
        Enum(Semester, native_enum=False), nullable=False
    )
    aktif: Mapped[bool] = mapped_column(Boolean, default=False)

    sekolah = relationship("Sekolah", back_populates="tahun_ajaran")
    kelas = relationship(
        "Kelas", back_populates="tahun_ajaran", cascade="all, delete-orphan"
    )
    nilai = relationship("Nilai", back_populates="tahun_ajaran")
    kenaikan_kelas = relationship(
        "KenaikanKelas",
        back_populates="tahun_ajaran_tujuan",
        foreign_keys="KenaikanKelas.tahun_ajaran_tujuan_id",
        cascade="all, delete-orphan",
    )
    kenaikan_kelas_asal = relationship(
        "KenaikanKelas",
        back_populates="tahun_ajaran_asal",
        foreign_keys="KenaikanKelas.tahun_ajaran_asal_id",
        cascade="all, delete-orphan",
    )


class Kelas(Base):
    __tablename__ = "kelas"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    tahun_ajaran_id: Mapped[str] = mapped_column(
        String, ForeignKey("tahun_ajaran.id", ondelete="CASCADE"), nullable=False
    )
    nama_kelas: Mapped[str] = mapped_column(String(100), nullable=False)
    tingkat: Mapped[int] = mapped_column(Integer, nullable=False)
    rombel: Mapped[str | None] = mapped_column(String(50))
    jurusan: Mapped[str | None] = mapped_column(String(100))
    wali_kelas_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("guru.id", ondelete="SET NULL")
    )
    kapasitas: Mapped[int | None] = mapped_column(Integer)

    sekolah = relationship("Sekolah", back_populates="kelas")
    tahun_ajaran = relationship("TahunAjaran", back_populates="kelas")
    wali_kelas = relationship("Guru", back_populates="wali_kelas_dari")
    anggota = relationship(
        "SiswaKelas", back_populates="kelas", cascade="all, delete-orphan"
    )
    relasi_mapel = relationship(
        "GuruMataPelajaran",
        back_populates="kelas",
        cascade="all, delete-orphan",
    )
    absensi = relationship("AbsensiSiswa", back_populates="kelas")
    nilai = relationship("Nilai", back_populates="kelas")


class GuruMataPelajaran(Base):
    __tablename__ = "guru_mata_pelajaran"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    guru_id: Mapped[str] = mapped_column(
        String, ForeignKey("guru.id", ondelete="CASCADE"), nullable=False
    )
    mata_pelajaran_id: Mapped[str] = mapped_column(
        String, ForeignKey("mata_pelajaran.id", ondelete="CASCADE"), nullable=False
    )
    kelas_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("kelas.id", ondelete="CASCADE")
    )

    guru = relationship("Guru", back_populates="mata_pelajaran_diampu")
    mata_pelajaran = relationship(
        "MataPelajaran", back_populates="relasi_guru"
    )
    kelas = relationship("Kelas", back_populates="relasi_mapel")


class TipePenilaian(PyEnum):
    pengetahuan = "pengetahuan"
    keterampilan = "keterampilan"
    sikap = "sikap"
    uts = "uts"
    uas = "uas"


class Nilai(Base):
    __tablename__ = "nilai"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    kelas_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("kelas.id", ondelete="SET NULL")
    )
    mata_pelajaran_id: Mapped[str] = mapped_column(
        String, ForeignKey("mata_pelajaran.id", ondelete="CASCADE"), nullable=False
    )
    guru_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("guru.id", ondelete="SET NULL")
    )
    tahun_ajaran_id: Mapped[str] = mapped_column(
        String, ForeignKey("tahun_ajaran.id", ondelete="CASCADE"), nullable=False
    )
    semester: Mapped[Semester] = mapped_column(
        Enum(Semester, native_enum=False), nullable=False
    )
    tipe_penilaian: Mapped[TipePenilaian] = mapped_column(
        Enum(TipePenilaian, native_enum=False), nullable=False
    )
    nilai_angka: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    nilai_huruf: Mapped[str | None] = mapped_column(String(5))
    deskripsi: Mapped[str | None] = mapped_column(Text)
    tanggal_penilaian: Mapped[date | None] = mapped_column(Date)

    siswa = relationship("Siswa", back_populates="nilai")
    kelas = relationship("Kelas", back_populates="nilai")
    mata_pelajaran = relationship("MataPelajaran", back_populates="nilai")
    guru = relationship("Guru", back_populates="nilai_diinput")
    tahun_ajaran = relationship("TahunAjaran", back_populates="nilai")
    sekolah = relationship("Sekolah", back_populates="nilai")


class StatusKehadiran(PyEnum):
    hadir = "hadir"
    sakit = "sakit"
    izin = "izin"
    alfa = "alfa"
    terlambat = "terlambat"


class AbsensiSiswa(Base):
    __tablename__ = "absensi_siswa"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sekolah_id: Mapped[str] = mapped_column(
        String, ForeignKey("sekolah.id", ondelete="CASCADE"), nullable=False
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    kelas_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("kelas.id", ondelete="SET NULL")
    )
    mata_pelajaran_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("mata_pelajaran.id", ondelete="SET NULL")
    )
    tanggal: Mapped[date] = mapped_column(Date, nullable=False)
    status_kehadiran: Mapped[StatusKehadiran] = mapped_column(
        Enum(StatusKehadiran, native_enum=False), nullable=False
    )
    keterangan: Mapped[str | None] = mapped_column(Text)
    dicatat_oleh_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("guru.id", ondelete="SET NULL")
    )
    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sekolah = relationship("Sekolah", back_populates="absensi")
    siswa = relationship("Siswa", back_populates="absensi")
    kelas = relationship("Kelas", back_populates="absensi")
    mata_pelajaran = relationship("MataPelajaran", back_populates="absensi")
    dicatat_oleh = relationship("Guru", back_populates="absensi_dicatat")


class StatusKenaikan(PyEnum):
    naik = "naik"
    tinggal = "tinggal"
    mutasi_keluar = "mutasi_keluar"


class KenaikanKelas(Base):
    __tablename__ = "kenaikan_kelas"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    siswa_id: Mapped[str] = mapped_column(
        String, ForeignKey("siswa.id", ondelete="CASCADE"), nullable=False
    )
    kelas_asal_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("kelas.id", ondelete="SET NULL")
    )
    kelas_tujuan_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("kelas.id", ondelete="SET NULL")
    )
    tahun_ajaran_asal_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("tahun_ajaran.id", ondelete="SET NULL")
    )
    tahun_ajaran_tujuan_id: Mapped[str] = mapped_column(
        String, ForeignKey("tahun_ajaran.id", ondelete="CASCADE"), nullable=False
    )
    status_kenaikan: Mapped[StatusKenaikan] = mapped_column(
        Enum(StatusKenaikan, native_enum=False), nullable=False
    )
    tanggal_keputusan: Mapped[date | None] = mapped_column(Date)
    catatan: Mapped[str | None] = mapped_column(Text)

    siswa = relationship("Siswa", back_populates="riwayat_kenaikan")
    tahun_ajaran_asal = relationship(
        "TahunAjaran",
        back_populates="kenaikan_kelas_asal",
        foreign_keys=[tahun_ajaran_asal_id],
    )
    tahun_ajaran_tujuan = relationship(
        "TahunAjaran",
        back_populates="kenaikan_kelas",
        foreign_keys=[tahun_ajaran_tujuan_id],
    )
    kelas_asal = relationship(
        "Kelas", foreign_keys=[kelas_asal_id]
    )
    kelas_tujuan = relationship(
        "Kelas", foreign_keys=[kelas_tujuan_id]
    )
