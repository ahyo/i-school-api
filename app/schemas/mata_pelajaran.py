from pydantic import BaseModel, Field, ConfigDict
from app.models.mata_pelajaran import KelompokMataPelajaran


class MataPelajaranBase(BaseModel):
    kode_mapel: str | None = Field(default=None, max_length=20)
    nama_mapel: str = Field(..., max_length=150)
    kelompok: KelompokMataPelajaran = KelompokMataPelajaran.umum
    tingkat_minimal: int | None = None
    tingkat_maksimal: int | None = None
    status_aktif: bool | None = True


class MataPelajaranCreate(MataPelajaranBase):
    pass


class MataPelajaranUpdate(BaseModel):
    kode_mapel: str | None = Field(default=None, max_length=20)
    nama_mapel: str | None = Field(default=None, max_length=150)
    kelompok: KelompokMataPelajaran | None = None
    tingkat_minimal: int | None = None
    tingkat_maksimal: int | None = None
    status_aktif: bool | None = None


class MataPelajaranDetail(MataPelajaranBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
