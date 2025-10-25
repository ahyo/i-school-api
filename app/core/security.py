from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
)

ALGORITHM = "HS256"


def buat_hash_kata_sandi(kata_sandi: str) -> str:
    return pwd_context.hash(kata_sandi)


def verifikasi_kata_sandi(kata_sandi: str, hash_sandi: str) -> bool:
    return pwd_context.verify(kata_sandi, hash_sandi)


def buat_token_akses(sub: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def parse_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
