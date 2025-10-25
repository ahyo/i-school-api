from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.pendaftaran import StatusPendaftaran
from app.models.referensi import JenisKelamin


class PendaftaranSiswaBase(BaseModel):
    nama_lengkap: str = Field(..., max_length=150)
    nama_panggilan: str | None = Field(default=None, max_length=50)
    jenis_kelamin: JenisKelamin
    tempat_lahir: str | None = Field(default=None, max_length=100)
    tanggal_lahir: date | None = None
    agama: str | None = Field(default=None, max_length=50)
    alamat: str | None = Field(default=None, max_length=255)
    asal_sekolah: str | None = Field(default=None, max_length=150)
    kelas_tujuan: str | None = Field(default=None, max_length=100)
    nomor_telepon: str | None = Field(default=None, max_length=25)
    email: EmailStr | None = None
    nama_ayah: str | None = Field(default=None, max_length=150)
    nama_ibu: str | None = Field(default=None, max_length=150)
    nomor_hp_wali: str | None = Field(default=None, max_length=25)
    catatan: str | None = Field(default=None, max_length=500)


class PendaftaranSiswaPublicCreate(PendaftaranSiswaBase):
    sekolah_id: str = Field(..., min_length=1)


class PendaftaranSiswaDetail(PendaftaranSiswaBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    status: StatusPendaftaran
    catatan_admin: str | None
    dibuat_pada: datetime
    diperbarui_pada: datetime


class PendaftaranSiswaUpdateStatus(BaseModel):
    status: StatusPendaftaran
    catatan_admin: str | None = Field(default=None, max_length=500)
