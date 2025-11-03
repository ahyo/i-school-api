from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from app.models.akademik import Semester
from app.models.siswa import StatusKeanggotaanKelas


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


class SiswaRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_lengkap: str
    nisn: str | None = None


class TahunAjaranRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_tahun: str
    semester_awal: Semester
    aktif: bool


class AnggotaKelasDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    siswa_id: str
    kelas_id: str
    status_keanggotaan: StatusKeanggotaanKelas
    tanggal_masuk: date | None = None
    tanggal_keluar: date | None = None
    siswa: SiswaRingkas


class MataPelajaranRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_mapel: str
    kode_mapel: str | None = None


class RelasiMapelDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    guru_id: str
    mata_pelajaran_id: str
    guru: GuruRingkas | None = None
    mata_pelajaran: MataPelajaranRingkas | None = None


class KelasBase(BaseModel):
    nama_kelas: str = Field(..., max_length=100)
    tingkat: int = Field(..., ge=1, le=13)
    rombel: str | None = Field(default=None, max_length=50)
    jurusan: str | None = Field(default=None, max_length=100)
    wali_kelas_id: str | None = None
    kapasitas: int | None = Field(default=None, ge=0)


class KelasCreate(KelasBase):
    tahun_ajaran_id: str


class KelasUpdate(BaseModel):
    nama_kelas: str | None = Field(default=None, max_length=100)
    tingkat: int | None = Field(default=None, ge=1, le=13)
    rombel: str | None = Field(default=None, max_length=50)
    jurusan: str | None = Field(default=None, max_length=100)
    wali_kelas_id: str | None = None
    kapasitas: int | None = Field(default=None, ge=0)


class KelasDetail(KelasBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    tahun_ajaran_id: str
    tahun_ajaran: TahunAjaranRingkas
    wali_kelas: GuruRingkas | None = None
    anggota: list[AnggotaKelasDetail] = Field(default_factory=list)
    relasi_mapel: list[RelasiMapelDetail] = Field(default_factory=list)
