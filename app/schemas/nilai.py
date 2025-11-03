from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.akademik import Semester, TipePenilaian
from app.schemas.siswa import SiswaRingkas


class NilaiCreate(BaseModel):
    siswa_id: str
    kelas_id: str | None = None
    mata_pelajaran_id: str
    guru_id: str | None = None
    tahun_ajaran_id: str
    semester: Semester
    tipe_penilaian: TipePenilaian
    nilai_angka: Decimal | None = Field(default=None, ge=0, le=100)
    nilai_huruf: str | None = Field(default=None, max_length=5)
    deskripsi: str | None = None
    tanggal_penilaian: date | None = None


class PenggunaRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_lengkap: str
    email: str
    status_aktif: bool


class GuruRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pengguna: PenggunaRingkas
    mata_pelajaran_utama: str | None = None


class KelasRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_kelas: str
    tingkat: int
    rombel: str | None = None


class MataPelajaranRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_mapel: str
    kode_mapel: str | None = None


class TahunAjaranRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_tahun: str
    semester_awal: Semester
    aktif: bool


class NilaiDetail(NilaiCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    siswa: SiswaRingkas
    kelas: KelasRingkas | None = None
    mata_pelajaran: MataPelajaranRingkas
    guru: GuruRingkas | None = None
    tahun_ajaran: TahunAjaranRingkas
