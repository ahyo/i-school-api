from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from app.models.akademik import Semester


class TahunAjaranBase(BaseModel):
    nama_tahun: str = Field(..., max_length=20)
    tanggal_mulai: date
    tanggal_selesai: date
    semester_awal: Semester
    aktif: bool | None = False


class TahunAjaranCreate(TahunAjaranBase):
    pass


class TahunAjaranUpdate(BaseModel):
    nama_tahun: str | None = Field(default=None, max_length=20)
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None
    semester_awal: Semester | None = None
    aktif: bool | None = None


class TahunAjaranDetail(TahunAjaranBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
