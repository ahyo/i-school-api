from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.siswa import Siswa
from app.models.akademik import Nilai, Kelas, TahunAjaran
from app.models.mata_pelajaran import MataPelajaran
from app.models.guru import Guru
from app.schemas.nilai import NilaiCreate, NilaiDetail
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(prefix="/nilai", tags=["Nilai"], route_class=EnvelopeAPIRoute)


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


@router.post("", response_model=NilaiDetail, status_code=status.HTTP_201_CREATED)
def tambah_nilai(
    payload: NilaiCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> Nilai:
    sekolah_id = _get_sekolah_id(pengguna)

    siswa = (
        db.query(Siswa)
        .filter(Siswa.id == payload.siswa_id, Siswa.sekolah_id == sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    mapel = (
        db.query(MataPelajaran)
        .filter(
            MataPelajaran.id == payload.mata_pelajaran_id,
            MataPelajaran.sekolah_id == sekolah_id,
        )
        .first()
    )
    if mapel is None:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    tahun_ajaran = (
        db.query(TahunAjaran)
        .filter(
            TahunAjaran.id == payload.tahun_ajaran_id,
            TahunAjaran.sekolah_id == sekolah_id,
        )
        .first()
    )
    if tahun_ajaran is None:
        raise HTTPException(status_code=404, detail="Tahun ajaran tidak ditemukan")

    kelas_id = payload.kelas_id
    if kelas_id:
        kelas = (
            db.query(Kelas)
            .filter(Kelas.id == kelas_id, Kelas.sekolah_id == sekolah_id)
            .first()
        )
        if kelas is None:
            raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    guru_id = payload.guru_id
    if pengguna.peran == PeranPengguna.guru:
        if pengguna.guru is None:
            raise HTTPException(status_code=403, detail="Akun guru belum lengkap")
        guru_id = pengguna.guru.id
    elif guru_id:
        guru = (
            db.query(Guru)
            .filter(Guru.id == guru_id, Guru.sekolah_id == sekolah_id)
            .first()
        )
        if guru is None:
            raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    nilai = Nilai(
        sekolah_id=sekolah_id,
        siswa_id=siswa.id,
        kelas_id=kelas_id,
        mata_pelajaran_id=mapel.id,
        guru_id=guru_id,
        tahun_ajaran_id=tahun_ajaran.id,
        semester=payload.semester,
        tipe_penilaian=payload.tipe_penilaian,
        nilai_angka=payload.nilai_angka,
        nilai_huruf=payload.nilai_huruf,
        deskripsi=payload.deskripsi,
        tanggal_penilaian=payload.tanggal_penilaian,
    )
    db.add(nilai)
    db.commit()
    db.refresh(nilai)
    return nilai


@router.get("", response_model=PaginatedResponse[NilaiDetail])
def daftar_nilai(
    siswa_id: str | None = Query(default=None),
    kelas_id: str | None = Query(default=None),
    mata_pelajaran_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> PaginatedResponse[NilaiDetail]:
    sekolah_id = _get_sekolah_id(pengguna)
    query = (
        db.query(Nilai)
        .options(
            selectinload(Nilai.siswa),
            selectinload(Nilai.kelas),
            selectinload(Nilai.mata_pelajaran),
            selectinload(Nilai.guru).selectinload(Guru.pengguna),
            selectinload(Nilai.tahun_ajaran),
        )
        .filter(Nilai.sekolah_id == sekolah_id)
    )
    if siswa_id:
        query = query.filter(Nilai.siswa_id == siswa_id)
    if kelas_id:
        query = query.filter(Nilai.kelas_id == kelas_id)
    if mata_pelajaran_id:
        query = query.filter(Nilai.mata_pelajaran_id == mata_pelajaran_id)
    query = query.order_by(Nilai.tanggal_penilaian.desc())
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[NilaiDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{nilai_id}", response_model=NilaiDetail)
def detail_nilai(
    nilai_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.guru)
    ),
) -> Nilai:
    nilai = (
        db.query(Nilai)
        .options(
            selectinload(Nilai.siswa),
            selectinload(Nilai.kelas),
            selectinload(Nilai.mata_pelajaran),
            selectinload(Nilai.guru).selectinload(Guru.pengguna),
            selectinload(Nilai.tahun_ajaran),
        )
        .filter(
            Nilai.id == nilai_id,
            Nilai.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if nilai is None:
        raise HTTPException(status_code=404, detail="Nilai tidak ditemukan")
    return nilai
