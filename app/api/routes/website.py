from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import (
    Pengguna,
    PeranPengguna,
    WebsiteKonten,
    JenisKonten,
    StatusKonten,
)
from app.schemas.website import (
    WebsiteKontenCreate,
    WebsiteKontenUpdate,
    WebsiteKontenDetail,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query
from app.utils.slug import buat_slug, slug_unik_generator
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/website", tags=["Website Sekolah"], route_class=EnvelopeAPIRoute
)


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


def _slug_exists(session: Session, sekolah_id: str, slug: str) -> bool:
    return (
        session.query(WebsiteKonten)
        .filter(
            WebsiteKonten.sekolah_id == sekolah_id,
            WebsiteKonten.slug == slug,
        )
        .first()
        is not None
    )


@router.post(
    "/konten",
    response_model=WebsiteKontenDetail,
    status_code=status.HTTP_201_CREATED,
)
def buat_konten(
    payload: WebsiteKontenCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> WebsiteKonten:
    sekolah_id = _get_sekolah_id(pengguna)
    base_slug = buat_slug(payload.judul)
    slug = slug_unik_generator(
        db,
        base_slug,
        lambda session, value: _slug_exists(session, sekolah_id, value),
    )

    tanggal_terbit = payload.tanggal_terbit
    if payload.status == StatusKonten.terbit and tanggal_terbit is None:
        tanggal_terbit = datetime.now(timezone.utc)

    konten = WebsiteKonten(
        sekolah_id=sekolah_id,
        penulis_id=pengguna.id,
        judul=payload.judul,
        slug=slug,
        jenis=payload.jenis,
        status=payload.status,
        ringkasan=payload.ringkasan,
        isi=payload.isi,
        banner_url=payload.banner_url,
        tag_meta=payload.tag_meta,
        tanggal_terbit=tanggal_terbit,
    )
    db.add(konten)
    db.commit()
    db.refresh(konten)
    return konten


@router.get("/konten", response_model=PaginatedResponse[WebsiteKontenDetail])
def daftar_konten_admin(
    status_konten: StatusKonten | None = Query(default=None),
    jenis: JenisKonten | None = Query(default=None),
    cari: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> PaginatedResponse[WebsiteKontenDetail]:
    sekolah_id = _get_sekolah_id(pengguna)
    query = (
        db.query(WebsiteKonten)
        .options(selectinload(WebsiteKonten.penulis))
        .filter(WebsiteKonten.sekolah_id == sekolah_id)
    )
    if status_konten:
        query = query.filter(WebsiteKonten.status == status_konten)
    if jenis:
        query = query.filter(WebsiteKonten.jenis == jenis)
    if cari:
        pattern = f"%{cari.lower()}%"
        query = query.filter(
            or_(
                WebsiteKonten.judul.ilike(pattern),
                WebsiteKonten.ringkasan.ilike(pattern),
            )
        )
    query = query.order_by(WebsiteKonten.dibuat_pada.desc())
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[WebsiteKontenDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/konten/{konten_id}",
    response_model=WebsiteKontenDetail,
)
def detail_konten_admin(
    konten_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> WebsiteKonten:
    konten = (
        db.query(WebsiteKonten)
        .options(selectinload(WebsiteKonten.penulis))
        .filter(
            WebsiteKonten.id == konten_id,
            WebsiteKonten.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if konten is None:
        raise HTTPException(status_code=404, detail="Konten tidak ditemukan")
    return konten


@router.put("/konten/{konten_id}", response_model=WebsiteKontenDetail)
def perbarui_konten(
    konten_id: str,
    payload: WebsiteKontenUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> WebsiteKonten:
    konten = (
        db.query(WebsiteKonten)
        .options(selectinload(WebsiteKonten.penulis))
        .filter(
            WebsiteKonten.id == konten_id,
            WebsiteKonten.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if konten is None:
        raise HTTPException(status_code=404, detail="Konten tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    judul_baru = data.pop("judul", None)
    perbarui_slug = data.pop("perbarui_slug", None)

    if judul_baru is not None:
        konten.judul = judul_baru
        if perbarui_slug:
            base_slug = buat_slug(judul_baru)
            slug = slug_unik_generator(
                db,
                base_slug,
                lambda session, value: _slug_exists(
                    session, konten.sekolah_id, value
                ),
            )
            konten.slug = slug

    for field, value in data.items():
        setattr(konten, field, value)

    if konten.status == StatusKonten.terbit and konten.tanggal_terbit is None:
        konten.tanggal_terbit = datetime.now(timezone.utc)

    konten.penulis_id = konten.penulis_id or pengguna.id
    db.add(konten)
    db.commit()
    db.refresh(konten)
    return konten


@router.delete("/konten/{konten_id}", status_code=status.HTTP_200_OK)
def hapus_konten(
    konten_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> dict[str, str]:
    konten = (
        db.query(WebsiteKonten)
        .filter(
            WebsiteKonten.id == konten_id,
            WebsiteKonten.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if konten is None:
        raise HTTPException(status_code=404, detail="Konten tidak ditemukan")

    db.delete(konten)
    db.commit()
    return {"message": "Konten berhasil dihapus"}


@router.get("/public/konten", response_model=PaginatedResponse[WebsiteKontenDetail])
def daftar_konten_public(
    sekolah_id: str,
    jenis: JenisKonten | None = Query(default=None),
    cari: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[WebsiteKontenDetail]:
    query = (
        db.query(WebsiteKonten)
        .options(selectinload(WebsiteKonten.penulis))
        .filter(
            WebsiteKonten.sekolah_id == sekolah_id,
            WebsiteKonten.status == StatusKonten.terbit,
        )
    )
    if jenis:
        query = query.filter(WebsiteKonten.jenis == jenis)
    if cari:
        pattern = f"%{cari.lower()}%"
        query = query.filter(
            or_(
                WebsiteKonten.judul.ilike(pattern),
                WebsiteKonten.ringkasan.ilike(pattern),
            )
        )
    query = query.order_by(WebsiteKonten.tanggal_terbit.desc(), WebsiteKonten.dibuat_pada.desc())

    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[WebsiteKontenDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/public/konten/{slug}", response_model=WebsiteKontenDetail)
def konten_by_slug(
    slug: str,
    sekolah_id: str,
    db: Session = Depends(get_db),
) -> WebsiteKonten:
    konten = (
        db.query(WebsiteKonten)
        .options(selectinload(WebsiteKonten.penulis))
        .filter(
            WebsiteKonten.slug == slug,
            WebsiteKonten.sekolah_id == sekolah_id,
            WebsiteKonten.status == StatusKonten.terbit,
        )
        .first()
    )
    if konten is None:
        raise HTTPException(status_code=404, detail="Konten tidak ditemukan")
    return konten
