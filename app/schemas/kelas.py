from pydantic import BaseModel, Field, ConfigDict


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
