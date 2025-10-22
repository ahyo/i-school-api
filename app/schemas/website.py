from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.website import JenisKonten, StatusKonten


class PenulisRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_lengkap: str
    email: str


class WebsiteKontenBase(BaseModel):
    judul: str = Field(..., max_length=200)
    jenis: JenisKonten
    status: StatusKonten = StatusKonten.draft
    ringkasan: str | None = Field(default=None, max_length=500)
    isi: str
    banner_url: str | None = Field(default=None, max_length=255)
    tag_meta: str | None = Field(default=None, max_length=255)
    tanggal_terbit: datetime | None = None


class WebsiteKontenCreate(WebsiteKontenBase):
    perbarui_slug: bool | None = False


class WebsiteKontenUpdate(BaseModel):
    judul: str | None = Field(default=None, max_length=200)
    jenis: JenisKonten | None = None
    status: StatusKonten | None = None
    ringkasan: str | None = Field(default=None, max_length=500)
    isi: str | None = None
    banner_url: str | None = Field(default=None, max_length=255)
    tag_meta: str | None = Field(default=None, max_length=255)
    tanggal_terbit: datetime | None = None
    perbarui_slug: bool | None = None


class WebsiteKontenDetail(WebsiteKontenBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    sekolah_id: str
    penulis: PenulisRingkas | None
    dibuat_pada: datetime
    diperbarui_pada: datetime
