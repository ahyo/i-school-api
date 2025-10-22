from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.mata_pelajaran import MataPelajaran
from app.schemas.mata_pelajaran import (
    MataPelajaranCreate,
    MataPelajaranDetail,
    MataPelajaranUpdate,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query


router = APIRouter(prefix="/mata-pelajaran", tags=["Mata Pelajaran"])


@router.post("", response_model=MataPelajaranDetail, status_code=status.HTTP_201_CREATED)
def tambah_mata_pelajaran(
    payload: MataPelajaranCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> MataPelajaran:
    mapel = MataPelajaran(
        sekolah_id=pengguna.sekolah_id,
        kode_mapel=payload.kode_mapel,
        nama_mapel=payload.nama_mapel,
        kelompok=payload.kelompok,
        tingkat_minimal=payload.tingkat_minimal,
        tingkat_maksimal=payload.tingkat_maksimal,
        status_aktif=payload.status_aktif if payload.status_aktif is not None else True,
    )
    db.add(mapel)
    db.commit()
    db.refresh(mapel)
    return mapel


@router.get("", response_model=PaginatedResponse[MataPelajaranDetail])
def daftar_mata_pelajaran(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[MataPelajaranDetail]:
    query = (
        db.query(MataPelajaran)
        .filter(MataPelajaran.sekolah_id == pengguna.sekolah_id)
        .order_by(MataPelajaran.nama_mapel.asc())
    )
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[MataPelajaranDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{mapel_id}", response_model=MataPelajaranDetail)
def detail_mata_pelajaran(
    mapel_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> MataPelajaran:
    mapel = (
        db.query(MataPelajaran)
        .filter(
            MataPelajaran.id == mapel_id,
            MataPelajaran.sekolah_id == pengguna.sekolah_id,
        )
        .first()
    )
    if mapel is None:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")
    return mapel


@router.put("/{mapel_id}", response_model=MataPelajaranDetail)
def perbarui_mata_pelajaran(
    mapel_id: str,
    payload: MataPelajaranUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> MataPelajaran:
    mapel = (
        db.query(MataPelajaran)
        .filter(
            MataPelajaran.id == mapel_id,
            MataPelajaran.sekolah_id == pengguna.sekolah_id,
        )
        .first()
    )
    if mapel is None:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(mapel, field, value)

    db.add(mapel)
    db.commit()
    db.refresh(mapel)
    return mapel
