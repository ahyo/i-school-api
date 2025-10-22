from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.akademik import Semester, TipePenilaian


class NilaiCreate(BaseModel):
    siswa_id: str
    kelas_id: str | None = None
    mata_pelajaran_id: str
    guru_id: str | None = None
    tahun_ajaran_id: str
    semester: Semester
    tipe_penilaian: TipePenilaian
    nilai_angka: Decimal | None = Field(default=None, ge=0, le=100)
    nilai_huruf: str | None = Field(default=None, max_length=5)
    deskripsi: str | None = None
    tanggal_penilaian: date | None = None


class NilaiDetail(NilaiCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
