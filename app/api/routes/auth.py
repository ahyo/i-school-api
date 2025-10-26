import logging
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
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
    TokenResetPassword,
    RefreshToken,
)
from app.schemas.auth import (
    RegistrasiAdminSekolah,
    ResponRegistrasiAdmin,
    PermintaanLogin,
    TokenResponse,
    PermintaanVerifikasiEmail,
    PenggunaProfile,
    PermintaanResetPassword,
    ResetPasswordKonfirmasi,
    RefreshTokenRequest,
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
    request: Request,
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

    access_token = buat_token_akses(sub=pengguna.id)
    refresh_token_str = secrets.token_urlsafe(48)
    refresh_record = RefreshToken(
        pengguna_id=pengguna.id,
        token=refresh_token_str,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        kedaluwarsa=datetime.now(timezone.utc)
        + timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    db.add(refresh_record)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


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


@router.post("/forgot-password", response_model=PesanResponse)
def forgot_password(
    payload: PermintaanResetPassword,
    db: Session = Depends(get_db),
) -> PesanResponse:
    pengguna = (
        db.query(Pengguna)
        .filter(Pengguna.email == payload.email, Pengguna.status_aktif.is_(True))
        .first()
    )

    if pengguna is None:
        # Balasan seragam untuk mencegah enumerasi akun
        return PesanResponse(pesan="Jika email terdaftar, tautan reset telah dikirim.")

    # Nonaktifkan token lama yang belum digunakan
    db.query(TokenResetPassword).filter(
        TokenResetPassword.pengguna_id == pengguna.id,
        TokenResetPassword.digunakan.is_(False),
    ).update({"digunakan": True}, synchronize_session=False)

    token_str = str(uuid.uuid4())
    token = TokenResetPassword(
        pengguna_id=pengguna.id,
        token=token_str,
        kedaluwarsa=datetime.now(timezone.utc) + timedelta(hours=2),
        digunakan=False,
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    reset_link = f"{settings.base_url}/reset-password?token={token.token}"
    email_content = f"""
        <p>Halo {pengguna.nama_lengkap},</p>
        <p>Kami menerima permintaan untuk mengatur ulang kata sandi akun Anda.</p>
        <p>Silakan klik tautan berikut untuk melanjutkan:</p>
        <p><a href=\"{reset_link}\">{reset_link}</a></p>
        <p>Jika Anda tidak meminta perubahan ini, abaikan email ini.</p>
        <p>Salam,<br />Tim {settings.app_nama}</p>
    """

    try:
        send_email(
            to_email=pengguna.email,
            subject="Reset Kata Sandi Akun",
            html_content=email_content,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gagal mengirim email reset password ke %s: %s", pengguna.email, exc)

    return PesanResponse(pesan="Jika email terdaftar, tautan reset telah dikirim.")


@router.post("/reset-password", response_model=PesanResponse)
def reset_password(
    payload: ResetPasswordKonfirmasi,
    db: Session = Depends(get_db),
) -> PesanResponse:
    token = (
        db.query(TokenResetPassword)
        .filter(
            TokenResetPassword.token == payload.token,
            TokenResetPassword.digunakan.is_(False),
        )
        .first()
    )
    if token is None or token.kedaluwarsa < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token reset password tidak valid atau kedaluwarsa")

    pengguna = db.query(Pengguna).filter(Pengguna.id == token.pengguna_id).first()
    if pengguna is None:
        raise HTTPException(status_code=400, detail="Pengguna tidak ditemukan")

    try:
        pengguna.kata_sandi_hash = buat_hash_kata_sandi(payload.kata_sandi_baru)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    token.digunakan = True
    db.query(RefreshToken).filter(
        RefreshToken.pengguna_id == pengguna.id,
        RefreshToken.dicabut.is_(False),
    ).update({"dicabut": True}, synchronize_session=False)

    db.add_all([pengguna, token])
    db.commit()

    return PesanResponse(pesan="Kata sandi berhasil diperbarui. Silakan login dengan kata sandi baru.")


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == payload.refresh_token,
            RefreshToken.dicabut.is_(False),
        )
        .first()
    )
    if record is None or record.kedaluwarsa < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token tidak valid atau kedaluwarsa")

    pengguna = (
        db.query(Pengguna)
        .filter(
            Pengguna.id == record.pengguna_id,
            Pengguna.status_aktif.is_(True),
        )
        .first()
    )
    if pengguna is None:
        raise HTTPException(status_code=401, detail="Pengguna tidak ditemukan atau tidak aktif")

    record.dicabut = True

    new_refresh_str = secrets.token_urlsafe(48)
    new_refresh = RefreshToken(
        pengguna_id=pengguna.id,
        token=new_refresh_str,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        kedaluwarsa=datetime.now(timezone.utc)
        + timedelta(minutes=settings.refresh_token_expire_minutes),
    )

    access_token = buat_token_akses(sub=pengguna.id)
    db.add_all([record, new_refresh])
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_str)


@router.post("/logout", response_model=PesanResponse)
def logout(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> PesanResponse:
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == payload.refresh_token)
        .first()
    )
    if record and not record.dicabut:
        record.dicabut = True
        db.add(record)
        db.commit()

    return PesanResponse(pesan="Logout berhasil.")
