from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.referensi import JenisKelamin
from app.models.siswa import StatusSiswa


class SiswaBase(BaseModel):
    nisn: str | None = Field(default=None, max_length=20)
    nis: str | None = Field(default=None, max_length=20)
    nama_lengkap: str = Field(..., max_length=150)
    nama_panggilan: str | None = Field(default=None, max_length=50)
    jenis_kelamin: JenisKelamin
    tempat_lahir: str | None = Field(default=None, max_length=100)
    tanggal_lahir: date | None = None
    agama: str | None = Field(default=None, max_length=50)
    alamat: str | None = Field(default=None, max_length=255)
    nomor_telepon: str | None = Field(default=None, max_length=25)
    nama_ayah: str | None = Field(default=None, max_length=150)
    nama_ibu: str | None = Field(default=None, max_length=150)
    wali_murid: str | None = Field(default=None, max_length=150)
    status_siswa: StatusSiswa = StatusSiswa.aktif
    tanggal_diterima: date | None = None
    catatan: str | None = Field(default=None, max_length=500)


class SiswaCreate(SiswaBase):
    kelas_id: str | None = None


class SiswaUpdate(BaseModel):
    nisn: str | None = Field(default=None, max_length=20)
    nis: str | None = Field(default=None, max_length=20)
    nama_lengkap: str | None = Field(default=None, max_length=150)
    nama_panggilan: str | None = Field(default=None, max_length=50)
    jenis_kelamin: JenisKelamin | None = None
    tempat_lahir: str | None = Field(default=None, max_length=100)
    tanggal_lahir: date | None = None
    agama: str | None = Field(default=None, max_length=50)
    alamat: str | None = Field(default=None, max_length=255)
    nomor_telepon: str | None = Field(default=None, max_length=25)
    nama_ayah: str | None = Field(default=None, max_length=150)
    nama_ibu: str | None = Field(default=None, max_length=150)
    wali_murid: str | None = Field(default=None, max_length=150)
    status_siswa: StatusSiswa | None = None
    tanggal_diterima: date | None = None
    catatan: str | None = Field(default=None, max_length=500)
    kelas_id: str | None = None


class SiswaDetail(SiswaBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    dibuat_pada: datetime
    diperbarui_pada: datetime


class SiswaRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_lengkap: str
    nisn: str | None = None
