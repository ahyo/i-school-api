from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna, CatatanSiswa, KategoriCatatan, Siswa
from app.schemas.catatan import CatatanSiswaCreate, CatatanSiswaDetail
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query


router = APIRouter(prefix="/catatan", tags=["Catatan Siswa"])


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


@router.post("", response_model=CatatanSiswaDetail, status_code=status.HTTP_201_CREATED)
def buat_catatan_siswa(
    payload: CatatanSiswaCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)),
) -> CatatanSiswa:
    sekolah_id = _get_sekolah_id(pengguna)
    siswa = (
        db.query(Siswa)
        .filter(Siswa.id == payload.siswa_id, Siswa.sekolah_id == sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    catatan = CatatanSiswa(
        sekolah_id=sekolah_id,
        siswa_id=siswa.id,
        kategori=payload.kategori,
        judul=payload.judul,
        isi=payload.isi,
        pencatat_id=pengguna.id,
    )
    db.add(catatan)
    db.commit()
    db.refresh(catatan)
    return catatan


@router.get("", response_model=PaginatedResponse[CatatanSiswaDetail])
def daftar_catatan_siswa(
    kategori: KategoriCatatan | None = Query(default=None),
    siswa_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)),
) -> PaginatedResponse[CatatanSiswaDetail]:
    sekolah_id = _get_sekolah_id(pengguna)
    query = (
        db.query(CatatanSiswa)
        .join(Siswa)
        .options(
            selectinload(CatatanSiswa.siswa),
            selectinload(CatatanSiswa.pencatat),
        )
        .filter(Siswa.sekolah_id == sekolah_id)
        .order_by(CatatanSiswa.dibuat_pada.desc())
    )
    if kategori:
        query = query.filter(CatatanSiswa.kategori == kategori)
    if siswa_id:
        query = query.filter(CatatanSiswa.siswa_id == siswa_id)

    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[CatatanSiswaDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{catatan_id}", response_model=CatatanSiswaDetail)
def detail_catatan_siswa(
    catatan_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)),
) -> CatatanSiswa:
    sekolah_id = _get_sekolah_id(pengguna)
    catatan = (
        db.query(CatatanSiswa)
        .join(Siswa)
        .options(
            selectinload(CatatanSiswa.siswa),
            selectinload(CatatanSiswa.pencatat),
        )
        .filter(
            CatatanSiswa.id == catatan_id,
            Siswa.sekolah_id == sekolah_id,
        )
        .first()
    )
    if catatan is None:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    return catatan
