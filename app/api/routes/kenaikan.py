from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.akademik import (
    KenaikanKelas,
    StatusKenaikan,
    Kelas,
    TahunAjaran,
)
from app.models.siswa import Siswa
from app.schemas.kenaikan import KenaikanKelasCreate, KenaikanKelasDetail
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/kenaikan", tags=["Kenaikan Kelas"], route_class=EnvelopeAPIRoute
)


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


@router.post(
    "",
    response_model=KenaikanKelasDetail,
    status_code=status.HTTP_201_CREATED,
)
def catat_kenaikan(
    payload: KenaikanKelasCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> KenaikanKelas:
    sekolah_id = _get_sekolah_id(pengguna)

    siswa = (
        db.query(Siswa)
        .filter(Siswa.id == payload.siswa_id, Siswa.sekolah_id == sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    if payload.kelas_asal_id:
        kelas_asal = (
            db.query(Kelas)
            .filter(
                Kelas.id == payload.kelas_asal_id,
                Kelas.sekolah_id == sekolah_id,
            )
            .first()
        )
        if kelas_asal is None:
            raise HTTPException(status_code=404, detail="Kelas asal tidak ditemukan")

    if payload.kelas_tujuan_id:
        kelas_tujuan = (
            db.query(Kelas)
            .filter(
                Kelas.id == payload.kelas_tujuan_id,
                Kelas.sekolah_id == sekolah_id,
            )
            .first()
        )
        if kelas_tujuan is None:
            raise HTTPException(status_code=404, detail="Kelas tujuan tidak ditemukan")

    if payload.tahun_ajaran_asal_id:
        tahun_asal = (
            db.query(TahunAjaran)
            .filter(
                TahunAjaran.id == payload.tahun_ajaran_asal_id,
                TahunAjaran.sekolah_id == sekolah_id,
            )
            .first()
        )
        if tahun_asal is None:
            raise HTTPException(status_code=404, detail="Tahun ajaran asal tidak ditemukan")

    tahun_tujuan = (
        db.query(TahunAjaran)
        .filter(
            TahunAjaran.id == payload.tahun_ajaran_tujuan_id,
            TahunAjaran.sekolah_id == sekolah_id,
        )
        .first()
    )
    if tahun_tujuan is None:
        raise HTTPException(status_code=404, detail="Tahun ajaran tujuan tidak ditemukan")

    kenaikan = KenaikanKelas(
        siswa_id=siswa.id,
        kelas_asal_id=payload.kelas_asal_id,
        kelas_tujuan_id=payload.kelas_tujuan_id,
        tahun_ajaran_asal_id=payload.tahun_ajaran_asal_id,
        tahun_ajaran_tujuan_id=payload.tahun_ajaran_tujuan_id,
        status_kenaikan=payload.status_kenaikan,
        tanggal_keputusan=payload.tanggal_keputusan,
        catatan=payload.catatan,
    )
    db.add(kenaikan)
    db.commit()
    db.refresh(kenaikan)
    return kenaikan


@router.get("", response_model=PaginatedResponse[KenaikanKelasDetail])
def daftar_kenaikan(
    status_kenaikan: StatusKenaikan | None = Query(default=None),
    siswa_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[KenaikanKelasDetail]:
    sekolah_id = _get_sekolah_id(pengguna)
    query = (
        db.query(KenaikanKelas)
        .join(Siswa)
        .options(
            selectinload(KenaikanKelas.siswa),
            selectinload(KenaikanKelas.kelas_asal),
            selectinload(KenaikanKelas.kelas_tujuan),
            selectinload(KenaikanKelas.tahun_ajaran_asal),
            selectinload(KenaikanKelas.tahun_ajaran_tujuan),
        )
        .filter(Siswa.sekolah_id == sekolah_id)
        .order_by(KenaikanKelas.tanggal_keputusan.desc().nullslast())
    )

    if status_kenaikan:
        query = query.filter(KenaikanKelas.status_kenaikan == status_kenaikan)
    if siswa_id:
        query = query.filter(KenaikanKelas.siswa_id == siswa_id)

    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[KenaikanKelasDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{kenaikan_id}", response_model=KenaikanKelasDetail)
def detail_kenaikan(
    kenaikan_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> KenaikanKelas:
    sekolah_id = _get_sekolah_id(pengguna)
    kenaikan = (
        db.query(KenaikanKelas)
        .join(Siswa)
        .options(
            selectinload(KenaikanKelas.siswa),
            selectinload(KenaikanKelas.kelas_asal),
            selectinload(KenaikanKelas.kelas_tujuan),
            selectinload(KenaikanKelas.tahun_ajaran_asal),
            selectinload(KenaikanKelas.tahun_ajaran_tujuan),
        )
        .filter(
            KenaikanKelas.id == kenaikan_id,
            Siswa.sekolah_id == sekolah_id,
        )
        .first()
    )
    if kenaikan is None:
        raise HTTPException(status_code=404, detail="Data kenaikan tidak ditemukan")
    return kenaikan
