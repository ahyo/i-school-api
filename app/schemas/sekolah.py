from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.sekolah import JenjangSekolah, StatusSekolah


class SekolahDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_sekolah: str
    npsn: str | None
    jenjang: JenjangSekolah
    status: StatusSekolah
    alamat_jalan: str | None
    kelurahan: str | None
    kecamatan: str | None
    kota_kabupaten: str | None
    provinsi: str | None
    kode_pos: str | None
    nomor_telepon: str | None
    email_resmi: str | None
    website: str | None
    kepala_sekolah: str | None
    tanggal_berdiri: datetime | None
    deskripsi: str | None
    status_verifikasi: bool
    dibuat_pada: datetime
    diperbarui_pada: datetime


class SekolahUpdate(BaseModel):
    nama_sekolah: str | None = Field(default=None, max_length=200)
    npsn: str | None = Field(default=None, max_length=20)
    alamat_jalan: str | None = Field(default=None, max_length=255)
    kelurahan: str | None = Field(default=None, max_length=100)
    kecamatan: str | None = Field(default=None, max_length=100)
    kota_kabupaten: str | None = Field(default=None, max_length=100)
    provinsi: str | None = Field(default=None, max_length=100)
    kode_pos: str | None = Field(default=None, max_length=10)
    nomor_telepon: str | None = Field(default=None, max_length=25)
    email_resmi: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=150)
    kepala_sekolah: str | None = Field(default=None, max_length=150)
    tanggal_berdiri: datetime | None = None
    deskripsi: str | None = Field(default=None, max_length=500)
