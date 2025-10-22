import calendar
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from app.core.deps import get_db, require_peran
from app.models import (
    Pengguna,
    PeranPengguna,
    Tagihan,
    JenisPembayaran,
    StatusTagihan,
    Siswa,
    StatusSiswa,
    SiswaKelas,
    StatusKeanggotaanKelas,
    StatusPembayaran,
)
from app.schemas.tagihan import (
    TagihanCreate,
    TagihanDetail,
    TagihanSPPGenerate,
    TagihanUpdate,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.utils.pagination import paginate_query


router = APIRouter(prefix="/tagihan", tags=["Tagihan"])


NAMA_BULAN_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}


def _get_sekolah_id(pengguna: Pengguna) -> str:
    if pengguna.sekolah_id is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak terhubung ke sekolah")
    return pengguna.sekolah_id


def _default_jatuh_tempo(tahun: int, bulan: int) -> date:
    hari = min(10, calendar.monthrange(tahun, bulan)[1])
    return date(tahun, bulan, hari)


def _refresh_status_tagihan(tagihan: Tagihan) -> None:
    total_dibayar = sum(
        (
            p.jumlah
            for p in tagihan.pembayaran
            if p.status_pembayaran == StatusPembayaran.lunas
        ),
        Decimal("0.00"),
    )
    tagihan.jumlah_terbayar = total_dibayar
    if total_dibayar >= tagihan.jumlah_tagihan:
        tagihan.status_tagihan = StatusTagihan.lunas
        tagihan.tanggal_lunas = tagihan.tanggal_lunas or date.today()
    elif total_dibayar > 0:
        tagihan.status_tagihan = StatusTagihan.sebagian
        tagihan.tanggal_lunas = None
    else:
        tagihan.status_tagihan = StatusTagihan.belum_dibayar
        tagihan.tanggal_lunas = None

    if (
        tagihan.status_tagihan != StatusTagihan.lunas
        and tagihan.tanggal_jatuh_tempo
        and tagihan.tanggal_jatuh_tempo < date.today()
    ):
        tagihan.status_tagihan = StatusTagihan.menunggak


@router.post("", response_model=TagihanDetail, status_code=status.HTTP_201_CREATED)
def buat_tagihan(
    payload: TagihanCreate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> Tagihan:
    sekolah_id = _get_sekolah_id(pengguna)
    siswa = (
        db.query(Siswa)
        .filter(Siswa.id == payload.siswa_id, Siswa.sekolah_id == sekolah_id)
        .first()
    )
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    tagihan = Tagihan(
        sekolah_id=sekolah_id,
        siswa_id=siswa.id,
        jenis_tagihan=payload.jenis_tagihan,
        nama_tagihan=payload.nama_tagihan,
        deskripsi=payload.deskripsi,
        jumlah_tagihan=payload.jumlah_tagihan,
        periode_bulan=payload.periode_bulan,
        periode_tahun=payload.periode_tahun,
        tanggal_jatuh_tempo=payload.tanggal_jatuh_tempo,
    )
    db.add(tagihan)
    db.commit()
    db.refresh(tagihan)
    return tagihan


@router.post("/spp", response_model=list[TagihanDetail])
def generate_tagihan_spp(
    payload: TagihanSPPGenerate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> list[Tagihan]:
    sekolah_id = _get_sekolah_id(pengguna)

    siswa_query = (
        db.query(Siswa)
        .filter(
            Siswa.sekolah_id == sekolah_id,
            Siswa.status_siswa == StatusSiswa.aktif,
        )
    )

    if payload.kelas_id:
        valid_kelas = (
            db.query(SiswaKelas)
            .join(Siswa, Siswa.id == SiswaKelas.siswa_id)
            .filter(
                SiswaKelas.kelas_id == payload.kelas_id,
                SiswaKelas.status_keanggotaan == StatusKeanggotaanKelas.aktif,
                Siswa.sekolah_id == sekolah_id,
            )
        )
        siswa_ids = {rel.siswa_id for rel in valid_kelas.all()}
        if not siswa_ids:
            return []
        siswa_query = siswa_query.filter(Siswa.id.in_(list(siswa_ids)))

    siswa_list = siswa_query.all()
    if not siswa_list:
        return []

    tanggal_jatuh_tempo = (
        payload.tanggal_jatuh_tempo or _default_jatuh_tempo(payload.tahun, payload.bulan)
    )
    nama_tagihan = f"SPP {NAMA_BULAN_ID[payload.bulan]} {payload.tahun}"

    created_tagihan: list[Tagihan] = []
    now = datetime.now()

    for siswa in siswa_list:
        existing = (
            db.query(Tagihan)
            .filter(
                Tagihan.sekolah_id == sekolah_id,
                Tagihan.siswa_id == siswa.id,
                Tagihan.jenis_tagihan == JenisPembayaran.spp,
                Tagihan.periode_bulan == payload.bulan,
                Tagihan.periode_tahun == payload.tahun,
            )
            .first()
        )
        if existing:
            continue

        tagihan = Tagihan(
            sekolah_id=sekolah_id,
            siswa_id=siswa.id,
            jenis_tagihan=JenisPembayaran.spp,
            nama_tagihan=nama_tagihan,
            jumlah_tagihan=payload.jumlah,
            periode_bulan=payload.bulan,
            periode_tahun=payload.tahun,
            tanggal_jatuh_tempo=tanggal_jatuh_tempo,
            dibuat_pada=now,
            diperbarui_pada=now,
        )
        db.add(tagihan)
        created_tagihan.append(tagihan)

    if created_tagihan:
        db.commit()
        for tagihan in created_tagihan:
            db.refresh(tagihan)

    return created_tagihan


@router.get("", response_model=PaginatedResponse[TagihanDetail])
def daftar_tagihan(
    status_tagihan: StatusTagihan | None = Query(default=None),
    jenis: JenisPembayaran | None = Query(default=None),
    bulan: int | None = Query(default=None, ge=1, le=12),
    tahun: int | None = Query(default=None, ge=2000, le=2100),
    siswa_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> PaginatedResponse[TagihanDetail]:
    query = (
        db.query(Tagihan)
        .options(selectinload(Tagihan.siswa))
        .filter(Tagihan.sekolah_id == _get_sekolah_id(pengguna))
    )

    if status_tagihan:
        query = query.filter(Tagihan.status_tagihan == status_tagihan)
    if jenis:
        query = query.filter(Tagihan.jenis_tagihan == jenis)
    if bulan:
        query = query.filter(Tagihan.periode_bulan == bulan)
    if tahun:
        query = query.filter(Tagihan.periode_tahun == tahun)
    if siswa_id:
        query = query.filter(Tagihan.siswa_id == siswa_id)

    query = query.order_by(Tagihan.tanggal_jatuh_tempo.asc())
    items, total, total_pages = paginate_query(query, page, limit)
    return PaginatedResponse[TagihanDetail](
        data=items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{tagihan_id}", response_model=TagihanDetail)
def detail_tagihan(
    tagihan_id: str,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> Tagihan:
    tagihan = (
        db.query(Tagihan)
        .options(selectinload(Tagihan.pembayaran))
        .filter(
            Tagihan.id == tagihan_id,
            Tagihan.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if tagihan is None:
        raise HTTPException(status_code=404, detail="Tagihan tidak ditemukan")
    return tagihan


@router.put("/{tagihan_id}", response_model=TagihanDetail)
def perbarui_tagihan(
    tagihan_id: str,
    payload: TagihanUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(
        require_peran(PeranPengguna.admin_sekolah, PeranPengguna.keuangan)
    ),
) -> Tagihan:
    tagihan = (
        db.query(Tagihan)
        .options(selectinload(Tagihan.pembayaran))
        .filter(
            Tagihan.id == tagihan_id,
            Tagihan.sekolah_id == _get_sekolah_id(pengguna),
        )
        .first()
    )
    if tagihan is None:
        raise HTTPException(status_code=404, detail="Tagihan tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    status_baru = data.pop("status_tagihan", None)

    for field, value in data.items():
        setattr(tagihan, field, value)

    if status_baru:
        tagihan.status_tagihan = status_baru
        if status_baru == StatusTagihan.lunas:
            tagihan.jumlah_terbayar = tagihan.jumlah_tagihan
            tagihan.tanggal_lunas = tagihan.tanggal_lunas or date.today()
        elif status_baru in (StatusTagihan.belum_dibayar, StatusTagihan.sebagian):
            tagihan.tanggal_lunas = None
        elif status_baru == StatusTagihan.menunggak and tagihan.jumlah_terbayar >= tagihan.jumlah_tagihan:
            tagihan.status_tagihan = StatusTagihan.lunas
    else:
        _refresh_status_tagihan(tagihan)
    db.add(tagihan)
    db.commit()
    db.refresh(tagihan)
    return tagihan
