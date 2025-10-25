from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from app.models.akademik import StatusKenaikan
from app.schemas.siswa import SiswaDetail
from app.schemas.kelas import KelasDetail
from app.schemas.tahun_ajaran import TahunAjaranDetail


class KenaikanKelasBase(BaseModel):
    siswa_id: str
    kelas_asal_id: str | None = None
    kelas_tujuan_id: str | None = None
    tahun_ajaran_asal_id: str | None = None
    tahun_ajaran_tujuan_id: str
    status_kenaikan: StatusKenaikan
    tanggal_keputusan: date | None = None
    catatan: str | None = Field(default=None, max_length=500)


class KenaikanKelasCreate(KenaikanKelasBase):
    pass


class KenaikanKelasDetail(KenaikanKelasBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    siswa: SiswaDetail
    kelas_asal: KelasDetail | None = None
    kelas_tujuan: KelasDetail | None = None
    tahun_ajaran_asal: TahunAjaranDetail | None = None
    tahun_ajaran_tujuan: TahunAjaranDetail
