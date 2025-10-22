from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.sekolah import JenjangSekolah, StatusSekolah


class RegistrasiAdminSekolah(BaseModel):
    nama_lengkap: str = Field(..., max_length=150)
    email: EmailStr
    kata_sandi: str = Field(..., min_length=8)
    nama_sekolah: str = Field(..., max_length=200)
    jenjang: JenjangSekolah
    status: StatusSekolah
    nomor_telepon: str | None = Field(default=None, max_length=25)
    alamat_jalan: str | None = Field(default=None, max_length=255)
    kelurahan: str | None = Field(default=None, max_length=100)
    kecamatan: str | None = Field(default=None, max_length=100)
    kota_kabupaten: str | None = Field(default=None, max_length=100)
    provinsi: str | None = Field(default=None, max_length=100)
    kode_pos: str | None = Field(default=None, max_length=10)


class ResponRegistrasiAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pengguna_id: str
    sekolah_id: str
    pesan: str


class PermintaanLogin(BaseModel):
    email: EmailStr
    kata_sandi: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PermintaanVerifikasiEmail(BaseModel):
    token: str
