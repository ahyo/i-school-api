from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_peran
from app.models import (
    Pengguna,
    PeranPengguna,
    Tagihan,
    Pembayaran,
    JenisPembayaran,
    StatusTagihan,
)
from app.models.pembayaran import StatusPembayaran
from app.schemas.laporan import LaporanPembayaranDetail
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/laporan", tags=["Laporan"], route_class=EnvelopeAPIRoute
)


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


@router.get("/pembayaran", response_model=LaporanPembayaranDetail)
def laporan_pembayaran(
    jenis: JenisPembayaran | None = Query(default=None),
    bulan: int | None = Query(default=None, ge=1, le=12),
    tahun: int | None = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> LaporanPembayaranDetail:
    sekolah_id = _get_sekolah_id(pengguna)

    tagihan_query = db.query(Tagihan).filter(Tagihan.sekolah_id == sekolah_id)
    if jenis:
        tagihan_query = tagihan_query.filter(Tagihan.jenis_tagihan == jenis)
    if bulan:
        tagihan_query = tagihan_query.filter(Tagihan.periode_bulan == bulan)
    if tahun:
        tagihan_query = tagihan_query.filter(Tagihan.periode_tahun == tahun)

    total_tagihan = tagihan_query.with_entities(
        func.coalesce(func.sum(Tagihan.jumlah_tagihan), 0)
    ).scalar() or Decimal("0.00")

    jumlah_tagihan = tagihan_query.with_entities(func.count(Tagihan.id)).scalar() or 0
    jumlah_tagihan_lunas = (
        tagihan_query.filter(Tagihan.status_tagihan == StatusTagihan.lunas)
        .with_entities(func.count(Tagihan.id))
        .scalar()
        or 0
    )

    pembayaran_query = (
        db.query(func.coalesce(func.sum(Pembayaran.jumlah), 0))
        .join(Tagihan, Pembayaran.tagihan_id == Tagihan.id, isouter=True)
        .filter(
            Pembayaran.sekolah_id == sekolah_id,
            Pembayaran.status_pembayaran == StatusPembayaran.lunas,
        )
    )

    if jenis:
        pembayaran_query = pembayaran_query.filter(
            Pembayaran.jenis_pembayaran == jenis
        )
    if bulan:
        pembayaran_query = pembayaran_query.filter(Tagihan.periode_bulan == bulan)
    if tahun:
        pembayaran_query = pembayaran_query.filter(Tagihan.periode_tahun == tahun)

    total_dibayar = pembayaran_query.scalar() or Decimal("0.00")

    if not isinstance(total_tagihan, Decimal):
        total_tagihan = Decimal(total_tagihan)
    if not isinstance(total_dibayar, Decimal):
        total_dibayar = Decimal(total_dibayar)

    total_sisa = total_tagihan - total_dibayar
    if total_sisa < Decimal("0"):
        total_sisa = Decimal("0.00")

    return LaporanPembayaranDetail(
        total_tagihan=total_tagihan,
        total_dibayar=total_dibayar,
        total_sisa=total_sisa,
        jumlah_tagihan=jumlah_tagihan,
        jumlah_tagihan_lunas=jumlah_tagihan_lunas,
        jumlah_tagihan_belum_lunas=jumlah_tagihan - jumlah_tagihan_lunas,
    )
