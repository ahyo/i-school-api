from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import SessionLocal
from app.core.security import parse_token
from app.models.pengguna import Pengguna, PeranPengguna


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_pengguna_aktif(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Pengguna:
    try:
        payload = parse_token(token)
        sub = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid")

    pengguna = (
        db.query(Pengguna)
        .filter(Pengguna.id == sub, Pengguna.status_aktif == True)
        .first()
    )
    if not pengguna:
        raise HTTPException(status_code=401, detail="Pengguna tidak ditemukan/aktif")
    return pengguna


def require_peran(*peran_diizinkan: PeranPengguna):
    def wrapper(pengguna: Pengguna = Depends(get_pengguna_aktif)):
        if pengguna.peran not in peran_diizinkan:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        return pengguna

    return wrapper
