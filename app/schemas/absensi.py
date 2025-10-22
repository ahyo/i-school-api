from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.akademik import StatusKehadiran


class AbsensiCreate(BaseModel):
    siswa_id: str
    kelas_id: str | None = None
    mata_pelajaran_id: str | None = None
    tanggal: date
    status_kehadiran: StatusKehadiran
    keterangan: str | None = Field(default=None, max_length=500)


class AbsensiDetail(AbsensiCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    dicatat_oleh_id: str | None
    dibuat_pada: datetime
