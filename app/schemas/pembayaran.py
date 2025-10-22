from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.pembayaran import JenisPembayaran, StatusPembayaran


class PembayaranCreate(BaseModel):
    siswa_id: str
    tagihan_id: str | None = None
    jenis_pembayaran: JenisPembayaran
    deskripsi: str | None = None
    periode: str | None = Field(default=None, max_length=20)
    jumlah: Decimal = Field(..., ge=0)
    tanggal_jatuh_tempo: date | None = None
    metode_pembayaran: str | None = Field(default=None, max_length=50)
    bukti_pembayaran_url: str | None = Field(default=None, max_length=255)
    keterangan: str | None = None


class PembayaranUpdateStatus(BaseModel):
    status_pembayaran: StatusPembayaran
    tanggal_bayar: date | None = None
    bukti_pembayaran_url: str | None = Field(default=None, max_length=255)
    keterangan: str | None = None


class PembayaranDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    siswa_id: str
    tagihan_id: str | None
    jenis_pembayaran: JenisPembayaran
    deskripsi: str | None
    periode: str | None
    jumlah: Decimal
    tanggal_jatuh_tempo: date | None
    tanggal_bayar: date | None
    status_pembayaran: StatusPembayaran
    metode_pembayaran: str | None
    bukti_pembayaran_url: str | None
    keterangan: str | None
    dicatat_pada: datetime
