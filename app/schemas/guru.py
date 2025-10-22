from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.guru import StatusGuru
from app.models.referensi import JenisKelamin


class PenggunaRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_lengkap: str
    email: EmailStr
    email_terverifikasi: bool
    status_aktif: bool


class GuruBase(BaseModel):
    nuptk: str | None = Field(default=None, max_length=20)
    nip: str | None = Field(default=None, max_length=20)
    tempat_lahir: str | None = Field(default=None, max_length=100)
    tanggal_lahir: date | None = None
    jenis_kelamin: JenisKelamin | None = None
    nomor_telepon: str | None = Field(default=None, max_length=25)
    alamat: str | None = Field(default=None, max_length=255)
    mata_pelajaran_utama: str | None = Field(default=None, max_length=100)
    status_guru: StatusGuru | None = None


class GuruCreate(GuruBase):
    nama_lengkap: str = Field(..., max_length=150)
    email: EmailStr
    kata_sandi: str = Field(..., min_length=8)


class GuruUpdate(GuruBase):
    status_guru: StatusGuru | None = None


class GuruDetail(GuruBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    pengguna: PenggunaRingkas
