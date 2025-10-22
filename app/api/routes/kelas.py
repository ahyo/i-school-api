from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.akademik import Kelas, TahunAjaran
from app.schemas.kelas import KelasCreate, KelasDetail, KelasUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query


router = APIRouter(prefix="/kelas", tags=["Kelas"])


@router.post("", response_model=KelasDetail, status_code=status.HTTP_201_CREATED)
def tambah_kelas(
    payload: KelasCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Kelas:
    tahun_ajaran = (
        db.query(TahunAjaran)
        .filter(
            TahunAjaran.id == payload.tahun_ajaran_id,
            TahunAjaran.sekolah_id == pengguna.sekolah_id,
        )
        .first()
    )
    if tahun_ajaran is None:
        raise HTTPException(status_code=404, detail="Tahun ajaran tidak ditemukan")

    kelas = Kelas(
        sekolah_id=pengguna.sekolah_id,
        tahun_ajaran_id=payload.tahun_ajaran_id,
        nama_kelas=payload.nama_kelas,
        tingkat=payload.tingkat,
        rombel=payload.rombel,
        jurusan=payload.jurusan,
        wali_kelas_id=payload.wali_kelas_id,
        kapasitas=payload.kapasitas,
    )
    db.add(kelas)
    db.commit()
    db.refresh(kelas)
    return kelas


@router.get("", response_model=PaginatedResponse[KelasDetail])
def daftar_kelas(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[KelasDetail]:
    query = (
        db.query(Kelas)
        .filter(Kelas.sekolah_id == pengguna.sekolah_id)
        .order_by(Kelas.tingkat.asc(), Kelas.nama_kelas.asc())
    )
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[KelasDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{kelas_id}", response_model=KelasDetail)
def detail_kelas(
    kelas_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Kelas:
    kelas = (
        db.query(Kelas)
        .options(selectinload(Kelas.anggota))
        .filter(Kelas.id == kelas_id, Kelas.sekolah_id == pengguna.sekolah_id)
        .first()
    )
    if kelas is None:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    return kelas


@router.put("/{kelas_id}", response_model=KelasDetail)
def ubah_kelas(
    kelas_id: str,
    payload: KelasUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Kelas:
    kelas = (
        db.query(Kelas)
        .filter(Kelas.id == kelas_id, Kelas.sekolah_id == pengguna.sekolah_id)
        .first()
    )
    if kelas is None:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    if "wali_kelas_id" in data and data["wali_kelas_id"] == "":
        data["wali_kelas_id"] = None

    for field, value in data.items():
        setattr(kelas, field, value)

    db.add(kelas)
    db.commit()
    db.refresh(kelas)
    return kelas
