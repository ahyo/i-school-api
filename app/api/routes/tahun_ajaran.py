from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.akademik import TahunAjaran
from app.schemas.tahun_ajaran import (
    TahunAjaranCreate,
    TahunAjaranDetail,
    TahunAjaranUpdate,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/tahun-ajaran", tags=["Tahun Ajaran"], route_class=EnvelopeAPIRoute
)


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


@router.post("", response_model=TahunAjaranDetail, status_code=status.HTTP_201_CREATED)
def tambah_tahun_ajaran(
    payload: TahunAjaranCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> TahunAjaran:
    sekolah_id = _get_sekolah_id(pengguna)
    if payload.aktif:
        db.query(TahunAjaran).filter(TahunAjaran.sekolah_id == sekolah_id).update(
            {"aktif": False}
        )

    tahun_ajaran = TahunAjaran(
        sekolah_id=sekolah_id,
        nama_tahun=payload.nama_tahun,
        tanggal_mulai=payload.tanggal_mulai,
        tanggal_selesai=payload.tanggal_selesai,
        semester_awal=payload.semester_awal,
        aktif=payload.aktif or False,
    )
    db.add(tahun_ajaran)
    db.commit()
    db.refresh(tahun_ajaran)
    return tahun_ajaran


@router.get("", response_model=PaginatedResponse[TahunAjaranDetail])
def daftar_tahun_ajaran(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> PaginatedResponse[TahunAjaranDetail]:
    query = (
        db.query(TahunAjaran)
        .filter(TahunAjaran.sekolah_id == _get_sekolah_id(pengguna))
        .order_by(TahunAjaran.tanggal_mulai.desc())
    )
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[TahunAjaranDetail](
        items=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{tahun_ajaran_id}", response_model=TahunAjaranDetail)
def detail_tahun_ajaran(
    tahun_ajaran_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> TahunAjaran:
    tahun_ajaran = (
        db.query(TahunAjaran)
        .filter(
            TahunAjaran.id == tahun_ajaran_id,
            TahunAjaran.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if tahun_ajaran is None:
        raise HTTPException(status_code=404, detail="Tahun ajaran tidak ditemukan")
    return tahun_ajaran


@router.put("/{tahun_ajaran_id}", response_model=TahunAjaranDetail)
def ubah_tahun_ajaran(
    tahun_ajaran_id: str,
    payload: TahunAjaranUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> TahunAjaran:
    tahun_ajaran = (
        db.query(TahunAjaran)
        .filter(
            TahunAjaran.id == tahun_ajaran_id,
            TahunAjaran.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if tahun_ajaran is None:
        raise HTTPException(status_code=404, detail="Tahun ajaran tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    if data.get("aktif"):
        db.query(TahunAjaran).filter(
            TahunAjaran.sekolah_id == tahun_ajaran.sekolah_id,
            TahunAjaran.id != tahun_ajaran.id,
        ).update({"aktif": False})

    for field, value in data.items():
        setattr(tahun_ajaran, field, value)

    db.add(tahun_ajaran)
    db.commit()
    db.refresh(tahun_ajaran)
    return tahun_ajaran
