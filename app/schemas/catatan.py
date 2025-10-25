from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.catatan import KategoriCatatan
from app.schemas.guru import PenggunaRingkas
from app.schemas.siswa import SiswaRingkas


class CatatanSiswaBase(BaseModel):
    siswa_id: str
    kategori: KategoriCatatan = KategoriCatatan.lainnya
    judul: str | None = Field(default=None, max_length=150)
    isi: str = Field(..., min_length=3)


class CatatanSiswaCreate(CatatanSiswaBase):
    pass


class CatatanSiswaDetail(CatatanSiswaBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    pencatat_id: str | None
    dibuat_pada: datetime
    siswa: SiswaRingkas
    pencatat: PenggunaRingkas | None = None
