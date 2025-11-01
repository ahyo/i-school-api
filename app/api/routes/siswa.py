from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import Pengguna, PeranPengguna
from app.models.siswa import Siswa, SiswaKelas, StatusKeanggotaanKelas
from app.models.akademik import Kelas
from app.schemas.siswa import SiswaCreate, SiswaDetail, SiswaUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(prefix="/siswa", tags=["Siswa"], route_class=EnvelopeAPIRoute)


@router.post("", response_model=SiswaDetail, status_code=status.HTTP_201_CREATED)
def tambah_siswa(
    payload: SiswaCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Siswa:
    kelas: Kelas | None = None
    if payload.kelas_id:
        kelas = (
            db.query(Kelas)
            .filter(Kelas.id == payload.kelas_id, Kelas.sekolah_id == pengguna.sekolah_id)
            .first()
        )
        if kelas is None:
            raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    siswa = Siswa(
        sekolah_id=pengguna.sekolah_id,
        nisn=payload.nisn,
        nis=payload.nis,
        nama_lengkap=payload.nama_lengkap,
        nama_panggilan=payload.nama_panggilan,
        jenis_kelamin=payload.jenis_kelamin,
        tempat_lahir=payload.tempat_lahir,
        tanggal_lahir=payload.tanggal_lahir,
        agama=payload.agama,
        alamat=payload.alamat,
        nomor_telepon=payload.nomor_telepon,
        nama_ayah=payload.nama_ayah,
        nama_ibu=payload.nama_ibu,
        wali_murid=payload.wali_murid,
        status_siswa=payload.status_siswa,
        tanggal_diterima=payload.tanggal_diterima,
        catatan=payload.catatan,
    )
    db.add(siswa)

    if kelas:
        siswa_kelas = SiswaKelas(
            siswa=siswa,
            kelas_id=kelas.id,
            status_keanggotaan=StatusKeanggotaanKelas.aktif,
            tanggal_masuk=payload.tanggal_diterima or date.today(),
        )
        db.add(siswa_kelas)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", "")
        if constraint_name == "uq_siswa_nisn":
            raise HTTPException(status_code=409, detail="NISN sudah digunakan") from exc
        raise HTTPException(status_code=400, detail="Gagal menambahkan siswa") from exc

    db.refresh(siswa)
    return siswa


@router.get("", response_model=PaginatedResponse[SiswaDetail])
def daftar_siswa(
    kelas_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[SiswaDetail]:
    query = (
        db.query(Siswa)
        .options(selectinload(Siswa.riwayat_kelas))
        .filter(Siswa.sekolah_id == pengguna.sekolah_id)
        .order_by(Siswa.nama_lengkap.asc())
    )
    if kelas_id:
        query = query.join(SiswaKelas).filter(
            SiswaKelas.kelas_id == kelas_id,
            SiswaKelas.status_keanggotaan == StatusKeanggotaanKelas.aktif,
        )
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[SiswaDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{siswa_id}", response_model=SiswaDetail)
def detail_siswa(
    siswa_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Siswa:
    siswa = (
        db.query(Siswa)
        .options(selectinload(Siswa.riwayat_kelas))
        .filter(Siswa.id == siswa_id, Siswa.sekolah_id == pengguna.sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    return siswa


@router.put("/{siswa_id}", response_model=SiswaDetail)
def ubah_siswa(
    siswa_id: str,
    payload: SiswaUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Siswa:
    siswa = (
        db.query(Siswa)
        .options(selectinload(Siswa.riwayat_kelas))
        .filter(Siswa.id == siswa_id, Siswa.sekolah_id == pengguna.sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    kelas_id_baru = data.pop("kelas_id", None)

    for field, value in data.items():
        setattr(siswa, field, value)

    if kelas_id_baru:
        kelas = (
            db.query(Kelas)
            .filter(Kelas.id == kelas_id_baru, Kelas.sekolah_id == pengguna.sekolah_id)
            .first()
        )
        if kelas is None:
            raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

        kelas_aktif = next(
            (
                rel
                for rel in siswa.riwayat_kelas
                if rel.status_keanggotaan == StatusKeanggotaanKelas.aktif
            ),
            None,
        )
        if kelas_aktif and kelas_aktif.kelas_id != kelas_id_baru:
            kelas_aktif.status_keanggotaan = StatusKeanggotaanKelas.pindah
            kelas_aktif.tanggal_keluar = date.today()
            db.add(kelas_aktif)

        siswa_kelas = SiswaKelas(
            siswa_id=siswa.id,
            kelas_id=kelas.id,
            status_keanggotaan=StatusKeanggotaanKelas.aktif,
            tanggal_masuk=date.today(),
        )
        db.add(siswa_kelas)

    db.add(siswa)
    db.commit()
    db.refresh(siswa)
    return siswa
