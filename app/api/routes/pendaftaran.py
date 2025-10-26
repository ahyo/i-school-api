from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_peran
from app.models import (
    Pengguna,
    PeranPengguna,
    PendaftaranSiswa,
    Sekolah,
    StatusPendaftaran,
)
from app.schemas.pendaftaran import (
    PendaftaranSiswaDetail,
    PendaftaranSiswaPublicCreate,
    PendaftaranSiswaUpdateStatus,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/pendaftaran",
    tags=["Pendaftaran Siswa"],
    route_class=EnvelopeAPIRoute,
)


@router.post(
    "/siswa",
    response_model=PendaftaranSiswaDetail,
    status_code=status.HTTP_201_CREATED,
)
def ajukan_pendaftaran(
    payload: PendaftaranSiswaPublicCreate,
    db: Session = Depends(get_db),
) -> PendaftaranSiswa:
    sekolah = db.query(Sekolah).filter(Sekolah.id == payload.sekolah_id).first()
    if sekolah is None:
        raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")

    data = payload.model_dump()
    sekolah_id = data.pop("sekolah_id")
    pendaftaran = PendaftaranSiswa(sekolah_id=sekolah_id, **data)
    db.add(pendaftaran)
    db.commit()
    db.refresh(pendaftaran)
    return pendaftaran


@router.get(
    "/siswa",
    response_model=PaginatedResponse[PendaftaranSiswaDetail],
)
def daftar_pendaftaran(
    status_pendaftaran: StatusPendaftaran | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[PendaftaranSiswaDetail]:
    query = (
        db.query(PendaftaranSiswa)
        .filter(PendaftaranSiswa.sekolah_id == pengguna.sekolah_id)
        .order_by(PendaftaranSiswa.dibuat_pada.desc())
    )
    if status_pendaftaran is not None:
        query = query.filter(PendaftaranSiswa.status == status_pendaftaran)

    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[PendaftaranSiswaDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/siswa/{pendaftaran_id}",
    response_model=PendaftaranSiswaDetail,
)
def detail_pendaftaran(
    pendaftaran_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PendaftaranSiswa:
    pendaftaran = (
        db.query(PendaftaranSiswa)
        .filter(
            PendaftaranSiswa.id == pendaftaran_id,
            PendaftaranSiswa.sekolah_id == pengguna.sekolah_id,
        )
        .first()
    )
    if pendaftaran is None:
        raise HTTPException(status_code=404, detail="Pendaftaran tidak ditemukan")
    return pendaftaran


@router.patch(
    "/siswa/{pendaftaran_id}/status",
    response_model=PendaftaranSiswaDetail,
)
def ubah_status_pendaftaran(
    pendaftaran_id: str,
    payload: PendaftaranSiswaUpdateStatus,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PendaftaranSiswa:
    pendaftaran = (
        db.query(PendaftaranSiswa)
        .filter(
            PendaftaranSiswa.id == pendaftaran_id,
            PendaftaranSiswa.sekolah_id == pengguna.sekolah_id,
        )
        .first()
    )
    if pendaftaran is None:
        raise HTTPException(status_code=404, detail="Pendaftaran tidak ditemukan")

    pendaftaran.status = payload.status
    pendaftaran.catatan_admin = payload.catatan_admin

    db.add(pendaftaran)
    db.commit()
    db.refresh(pendaftaran)
    return pendaftaran
