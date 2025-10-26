from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.core.security import buat_hash_kata_sandi
from app.models import Pengguna, Guru, PeranPengguna
from app.models.guru import StatusGuru
from app.schemas.guru import GuruCreate, GuruDetail, GuruUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(prefix="/guru", tags=["Guru"], route_class=EnvelopeAPIRoute)


@router.post("", response_model=GuruDetail, status_code=status.HTTP_201_CREATED)
def tambah_guru(
    payload: GuruCreate,
    db: Session = Depends(get_db),
    admin: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Guru:
    if (
        db.query(Pengguna)
        .filter(Pengguna.email == payload.email)
        .first()
        is not None
    ):
        raise HTTPException(status_code=400, detail="Email guru sudah digunakan")

    try:
        kata_sandi_hash = buat_hash_kata_sandi(payload.kata_sandi)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    pengguna = Pengguna(
        nama_lengkap=payload.nama_lengkap,
        email=payload.email,
        kata_sandi_hash=kata_sandi_hash,
        peran=PeranPengguna.guru,
        email_terverifikasi=True,
        status_aktif=True,
        sekolah_id=admin.sekolah_id,
    )

    guru = Guru(
        pengguna=pengguna,
        sekolah_id=admin.sekolah_id,
        nuptk=payload.nuptk,
        nip=payload.nip,
        tempat_lahir=payload.tempat_lahir,
        tanggal_lahir=payload.tanggal_lahir,
        jenis_kelamin=payload.jenis_kelamin,
        nomor_telepon=payload.nomor_telepon,
        alamat=payload.alamat,
        mata_pelajaran_utama=payload.mata_pelajaran_utama,
        status_guru=payload.status_guru or StatusGuru.aktif,
    )

    db.add_all([pengguna, guru])
    db.commit()
    db.refresh(guru)
    return guru


@router.get("", response_model=PaginatedResponse[GuruDetail])
def daftar_guru(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[GuruDetail]:
    query = (
        db.query(Guru)
        .options(selectinload(Guru.pengguna))
        .join(Guru.pengguna)
        .filter(Guru.sekolah_id == pengguna.sekolah_id)
        .order_by(Pengguna.nama_lengkap.asc())
    )
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[GuruDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{guru_id}", response_model=GuruDetail)
def detail_guru(
    guru_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Guru:
    guru = (
        db.query(Guru)
        .options(selectinload(Guru.pengguna))
        .filter(Guru.id == guru_id, Guru.sekolah_id == pengguna.sekolah_id)
        .first()
    )
    if guru is None:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
    return guru


@router.put("/{guru_id}", response_model=GuruDetail)
def ubah_data_guru(
    guru_id: str,
    payload: GuruUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Guru:
    guru = (
        db.query(Guru)
        .options(selectinload(Guru.pengguna))
        .filter(Guru.id == guru_id, Guru.sekolah_id == pengguna.sekolah_id)
        .first()
    )
    if guru is None:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(guru, field, value)

    db.add(guru)
    db.commit()
    db.refresh(guru)
    return guru
