from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.pembayaran import (
    Pembayaran,
    Tagihan,
    StatusPembayaran,
    StatusTagihan,
)
from app.models.siswa import Siswa
from app.schemas.pembayaran import (
    PembayaranCreate,
    PembayaranDetail,
    PembayaranUpdateStatus,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query


router = APIRouter(prefix="/pembayaran", tags=["Pembayaran"])


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id

def _recalculate_tagihan(tagihan: Tagihan) -> None:
    total_lunas = sum(
        (p.jumlah for p in tagihan.pembayaran if p.status_pembayaran == StatusPembayaran.lunas),
        Decimal("0.00"),
    )
    tagihan.jumlah_terbayar = total_lunas

    if total_lunas >= tagihan.jumlah_tagihan:
        tagihan.status_tagihan = StatusTagihan.lunas
        tagihan.tanggal_lunas = tagihan.tanggal_lunas or date.today()
    elif total_lunas > 0:
        tagihan.status_tagihan = StatusTagihan.sebagian
        tagihan.tanggal_lunas = None
    else:
        tagihan.status_tagihan = StatusTagihan.belum_dibayar
        tagihan.tanggal_lunas = None

    if (
        tagihan.status_tagihan != StatusTagihan.lunas
        and tagihan.tanggal_jatuh_tempo
        and tagihan.tanggal_jatuh_tempo < date.today()
    ):
        tagihan.status_tagihan = StatusTagihan.menunggak


@router.post("", response_model=PembayaranDetail, status_code=status.HTTP_201_CREATED)
def catat_pembayaran(
    payload: PembayaranCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> Pembayaran:
    sekolah_id = _get_sekolah_id(pengguna)
    siswa = (
        db.query(Siswa)
        .filter(Siswa.id == payload.siswa_id, Siswa.sekolah_id == sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    tagihan: Tagihan | None = None
    if payload.tagihan_id:
        tagihan = (
            db.query(Tagihan)
            .options(selectinload(Tagihan.pembayaran))
            .filter(
                Tagihan.id == payload.tagihan_id,
                Tagihan.sekolah_id == sekolah_id,
            )
            .first()
        )
        if tagihan is None:
            raise HTTPException(status_code=404, detail="Tagihan tidak ditemukan")
        if tagihan.siswa_id != siswa.id:
            raise HTTPException(
                status_code=400, detail="Tagihan tidak sesuai dengan siswa yang dipilih"
            )
        if payload.jenis_pembayaran != tagihan.jenis_tagihan:
            raise HTTPException(
                status_code=400,
                detail="Jenis pembayaran harus sesuai dengan jenis tagihan",
            )
        if tagihan.status_tagihan == StatusTagihan.lunas:
            raise HTTPException(status_code=400, detail="Tagihan sudah lunas")

    pembayaran = Pembayaran(
        sekolah_id=sekolah_id,
        siswa_id=siswa.id,
        tagihan_id=tagihan.id if tagihan else None,
        jenis_pembayaran=payload.jenis_pembayaran,
        deskripsi=payload.deskripsi,
        periode=payload.periode,
        jumlah=payload.jumlah,
        tanggal_jatuh_tempo=payload.tanggal_jatuh_tempo,
        metode_pembayaran=payload.metode_pembayaran,
        bukti_pembayaran_url=payload.bukti_pembayaran_url,
        keterangan=payload.keterangan,
    )
    db.add(pembayaran)
    if tagihan and not pembayaran.tanggal_jatuh_tempo:
        pembayaran.tanggal_jatuh_tempo = tagihan.tanggal_jatuh_tempo

    db.commit()
    db.refresh(pembayaran)
    return pembayaran


@router.get("", response_model=PaginatedResponse[PembayaranDetail])
def daftar_pembayaran(
    siswa_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> PaginatedResponse[PembayaranDetail]:
    query = (
        db.query(Pembayaran)
        .filter(Pembayaran.sekolah_id == _get_sekolah_id(pengguna))
        .order_by(Pembayaran.dicatat_pada.desc())
    )
    if siswa_id:
        query = query.filter(Pembayaran.siswa_id == siswa_id)
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[PembayaranDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{pembayaran_id}", response_model=PembayaranDetail)
def detail_pembayaran(
    pembayaran_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> Pembayaran:
    pembayaran = (
        db.query(Pembayaran)
        .options(selectinload(Pembayaran.tagihan))
        .filter(
            Pembayaran.id == pembayaran_id,
            Pembayaran.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if pembayaran is None:
        raise HTTPException(status_code=404, detail="Data pembayaran tidak ditemukan")
    return pembayaran


@router.put("/{pembayaran_id}", response_model=PembayaranDetail)
def perbarui_status_pembayaran(
    pembayaran_id: str,
    payload: PembayaranUpdateStatus,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> Pembayaran:
    pembayaran = (
        db.query(Pembayaran)
        .options(selectinload(Pembayaran.tagihan))
        .filter(
            Pembayaran.id == pembayaran_id,
            Pembayaran.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if pembayaran is None:
        raise HTTPException(status_code=404, detail="Data pembayaran tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(pembayaran, field, value)

    if (
        pembayaran.status_pembayaran == StatusPembayaran.lunas
        and pembayaran.tanggal_bayar is None
    ):
        pembayaran.tanggal_bayar = date.today()

    if pembayaran.tagihan:
        _recalculate_tagihan(pembayaran.tagihan)
        db.add(pembayaran.tagihan)

    db.add(pembayaran)
    db.commit()
    db.refresh(pembayaran)
    if pembayaran.tagihan:
        db.refresh(pembayaran.tagihan)
    return pembayaran
