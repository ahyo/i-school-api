from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.pembayaran import JenisPembayaran, StatusTagihan
from app.models.pembayaran import StatusPembayaran
from app.schemas.siswa import SiswaRingkas


class PembayaranRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    jenis_pembayaran: JenisPembayaran
    jumlah: Decimal
    status_pembayaran: StatusPembayaran
    tanggal_bayar: date | None = None
    tagihan_id: str | None = None


class TagihanBase(BaseModel):
    jenis_tagihan: JenisPembayaran
    nama_tagihan: str = Field(..., max_length=150)
    deskripsi: str | None = None
    jumlah_tagihan: Decimal = Field(..., ge=0)
    periode_bulan: int | None = Field(default=None, ge=1, le=12)
    periode_tahun: int | None = Field(default=None, ge=2000, le=2100)
    tanggal_jatuh_tempo: date | None = None


class TagihanCreate(TagihanBase):
    siswa_id: str


class TagihanSPPGenerate(BaseModel):
    bulan: int = Field(..., ge=1, le=12)
    tahun: int = Field(..., ge=2000, le=2100)
    jumlah: Decimal = Field(..., ge=0)
    tanggal_jatuh_tempo: date | None = None
    kelas_id: str | None = None


class TagihanUpdate(BaseModel):
    nama_tagihan: str | None = Field(default=None, max_length=150)
    deskripsi: str | None = None
    jumlah_tagihan: Decimal | None = Field(default=None, ge=0)
    tanggal_jatuh_tempo: date | None = None
    status_tagihan: StatusTagihan | None = None


class TagihanDetail(TagihanBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    siswa_id: str
    jumlah_terbayar: Decimal
    status_tagihan: StatusTagihan
    tanggal_lunas: date | None
    tanggal_tagihan: date
    dibuat_pada: datetime
    diperbarui_pada: datetime
    siswa: SiswaRingkas
    pembayaran: list[PembayaranRingkas] = Field(default_factory=list)
