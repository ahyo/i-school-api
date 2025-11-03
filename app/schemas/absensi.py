from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.akademik import StatusKehadiran
from app.schemas.siswa import SiswaRingkas


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


class AbsensiCreate(BaseModel):
    siswa_id: str
    kelas_id: str | None = None
    mata_pelajaran_id: str | None = None
    tanggal: date
    status_kehadiran: StatusKehadiran
    keterangan: str | None = Field(default=None, max_length=500)


class AbsensiDetail(AbsensiCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    dicatat_oleh_id: str | None
    dibuat_pada: datetime
    siswa: SiswaRingkas
    kelas: KelasRingkas | None = None
    mata_pelajaran: MataPelajaranRingkas | None = None
    dicatat_oleh: GuruRingkas | None = None
