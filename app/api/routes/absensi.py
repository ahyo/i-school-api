from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.akademik import AbsensiSiswa, Kelas
from app.models.siswa import Siswa
from app.models.mata_pelajaran import MataPelajaran
from app.models.guru import Guru
from app.schemas.absensi import AbsensiCreate, AbsensiDetail
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/absensi", tags=["Absensi"], route_class=EnvelopeAPIRoute
)


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


@router.post("", response_model=AbsensiDetail, status_code=status.HTTP_201_CREATED)
def catat_absensi(
    payload: AbsensiCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> AbsensiSiswa:
    sekolah_id = _get_sekolah_id(pengguna)
    siswa = (
        db.query(Siswa)
        .filter(Siswa.id == payload.siswa_id, Siswa.sekolah_id == sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    kelas_id = payload.kelas_id
    if kelas_id:
        kelas = (
            db.query(Kelas)
            .filter(Kelas.id == kelas_id, Kelas.sekolah_id == sekolah_id)
            .first()
        )
        if kelas is None:
            raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    mata_pelajaran_id = payload.mata_pelajaran_id
    if mata_pelajaran_id:
        mapel = (
            db.query(MataPelajaran)
            .filter(
                MataPelajaran.id == mata_pelajaran_id,
                MataPelajaran.sekolah_id == sekolah_id,
            )
            .first()
        )
        if mapel is None:
            raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    dicatat_oleh_id = None
    if pengguna.peran == PeranPengguna.guru:
        if pengguna.guru is None:
            raise HTTPException(status_code=403, detail="Data guru belum lengkap")
        dicatat_oleh_id = pengguna.guru.id

    absensi = AbsensiSiswa(
        sekolah_id=sekolah_id,
        siswa_id=siswa.id,
        kelas_id=kelas_id,
        mata_pelajaran_id=mata_pelajaran_id,
        tanggal=payload.tanggal,
        status_kehadiran=payload.status_kehadiran,
        keterangan=payload.keterangan,
        dicatat_oleh_id=dicatat_oleh_id,
    )
    db.add(absensi)
    db.commit()
    db.refresh(absensi)
    return absensi


@router.get("", response_model=PaginatedResponse[AbsensiDetail])
def daftar_absensi(
    tanggal: date | None = Query(default=None),
    siswa_id: str | None = Query(default=None),
    kelas_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> PaginatedResponse[AbsensiDetail]:
    sekolah_id = _get_sekolah_id(pengguna)
    query = (
        db.query(AbsensiSiswa)
        .options(
            selectinload(AbsensiSiswa.siswa),
            selectinload(AbsensiSiswa.kelas),
            selectinload(AbsensiSiswa.mata_pelajaran),
            selectinload(AbsensiSiswa.dicatat_oleh).selectinload(Guru.pengguna),
        )
        .filter(AbsensiSiswa.sekolah_id == sekolah_id)
    )
    if tanggal:
        query = query.filter(AbsensiSiswa.tanggal == tanggal)
    if siswa_id:
        query = query.filter(AbsensiSiswa.siswa_id == siswa_id)
    if kelas_id:
        query = query.filter(AbsensiSiswa.kelas_id == kelas_id)
    query = query.order_by(AbsensiSiswa.tanggal.desc())
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[AbsensiDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{absensi_id}", response_model=AbsensiDetail)
def detail_absensi(
    absensi_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> AbsensiSiswa:
    absensi = (
        db.query(AbsensiSiswa)
        .options(
            selectinload(AbsensiSiswa.siswa),
            selectinload(AbsensiSiswa.kelas),
            selectinload(AbsensiSiswa.mata_pelajaran),
            selectinload(AbsensiSiswa.dicatat_oleh).selectinload(Guru.pengguna),
        )
        .filter(
            AbsensiSiswa.id == absensi_id,
            AbsensiSiswa.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if absensi is None:
        raise HTTPException(status_code=404, detail="Absensi tidak ditemukan")
    return absensi
