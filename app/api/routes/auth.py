import logging
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_pengguna_aktif
from app.core.config import settings
from app.core.security import (
    buat_hash_kata_sandi,
    verifikasi_kata_sandi,
    buat_token_akses,
)
from app.models import (
    Pengguna,
    Sekolah,
    TokenVerifikasiEmail,
    PeranPengguna,
)
from app.schemas.auth import (
    RegistrasiAdminSekolah,
    ResponRegistrasiAdmin,
    PermintaanLogin,
    TokenResponse,
    PermintaanVerifikasiEmail,
    PenggunaProfile,
)
from app.schemas.common import PesanResponse
from app.models.sekolah import StatusSekolah
from app.utils.email import send_email


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["Autentikasi"])


@router.post(
    "/register-admin",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponRegistrasiAdmin,
)
def register_admin_sekolah(
    payload: RegistrasiAdminSekolah, db: Session = Depends(get_db)
) -> ResponRegistrasiAdmin:
    if (
        db.query(Pengguna)
        .filter(Pengguna.email == payload.email)
        .first()
        is not None
    ):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    sekolah = Sekolah(
        nama_sekolah=payload.nama_sekolah,
        jenjang=payload.jenjang,
        status=payload.status or StatusSekolah.negeri,
        nomor_telepon=payload.nomor_telepon,
        alamat_jalan=payload.alamat_jalan,
        kelurahan=payload.kelurahan,
        kecamatan=payload.kecamatan,
        kota_kabupaten=payload.kota_kabupaten,
        provinsi=payload.provinsi,
        kode_pos=payload.kode_pos,
        status_verifikasi=False,
    )

    try:
        kata_sandi_hash = buat_hash_kata_sandi(payload.kata_sandi)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    pengguna = Pengguna(
        nama_lengkap=payload.nama_lengkap,
        email=payload.email,
        kata_sandi_hash=kata_sandi_hash,
        peran=PeranPengguna.admin_sekolah,
        email_terverifikasi=False,
        status_aktif=True,
        sekolah=sekolah,
    )

    token = TokenVerifikasiEmail(
        pengguna=pengguna,
        token=str(uuid.uuid4()),
        kedaluwarsa=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add_all([sekolah, pengguna, token])
    db.commit()
    db.refresh(pengguna)
    db.refresh(sekolah)

    try:
        verification_link = (
            f"{settings.base_url}/auth/verify-email?token={token.token}"
        )
        email_content = f"""
            <p>Halo {payload.nama_lengkap},</p>
            <p>Terima kasih telah mendaftar sebagai admin sekolah pada <strong>{settings.app_nama}</strong>.</p>
            <p>Silakan verifikasi email Anda dengan mengunjungi tautan berikut:</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p>Atau gunakan token berikut melalui aplikasi:</p>
            <p><code>{token.token}</code></p>
            <p>Salam hangat,<br />Tim {settings.app_nama}</p>
        """
        send_email(
            to_email=payload.email,
            subject="Verifikasi Email Admin Sekolah",
            html_content=email_content,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Gagal mengirim email verifikasi ke %s: %s", payload.email, exc
        )

    return ResponRegistrasiAdmin(
        pengguna_id=pengguna.id,
        sekolah_id=sekolah.id,
        pesan="Registrasi berhasil. Silakan cek email untuk verifikasi.",
    )


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: PermintaanLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    pengguna = (
        db.query(Pengguna)
        .filter(Pengguna.email == credentials.email)
        .first()
    )
    if pengguna is None:
        raise HTTPException(status_code=401, detail="Email atau kata sandi salah")
    try:
        valid = verifikasi_kata_sandi(credentials.kata_sandi, pengguna.kata_sandi_hash)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not valid:
        raise HTTPException(status_code=401, detail="Email atau kata sandi salah")
    if not pengguna.status_aktif:
        raise HTTPException(status_code=403, detail="Akun tidak aktif")
    if not pengguna.email_terverifikasi:
        raise HTTPException(status_code=403, detail="Email belum diverifikasi")

    token = buat_token_akses(sub=pengguna.id)
    return TokenResponse(access_token=token)


@router.post("/verifikasi-email", response_model=PesanResponse)
def verifikasi_email(
    payload: PermintaanVerifikasiEmail, db: Session = Depends(get_db)
) -> PesanResponse:
    token = (
        db.query(TokenVerifikasiEmail)
        .filter(
            TokenVerifikasiEmail.token == payload.token,
            TokenVerifikasiEmail.digunakan.is_(False),
            TokenVerifikasiEmail.kedaluwarsa >= datetime.now(timezone.utc),
        )
        .first()
    )
    if token is None:
        raise HTTPException(status_code=400, detail="Token verifikasi tidak valid")

    pengguna = db.get(Pengguna, token.pengguna_id)
    if pengguna is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak ditemukan")

    pengguna.email_terverifikasi = True
    token.digunakan = True
    db.commit()

    return PesanResponse(pesan="Email berhasil diverifikasi. Silakan login.")


@router.get("/me", response_model=PenggunaProfile)
def profil_pengguna(pengguna: Pengguna = Depends(get_pengguna_aktif)) -> Pengguna:
    return pengguna
