from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.pembayaran import JenisPembayaran


class LaporanPembayaranFilter(BaseModel):
    jenis: JenisPembayaran | None = None
    bulan: int | None = Field(default=None, ge=1, le=12)
    tahun: int | None = Field(default=None, ge=2000, le=2100)


class LaporanPembayaranDetail(BaseModel):
    total_tagihan: Decimal
    total_dibayar: Decimal
    total_sisa: Decimal
    jumlah_tagihan: int
    jumlah_tagihan_lunas: int
    jumlah_tagihan_belum_lunas: int
