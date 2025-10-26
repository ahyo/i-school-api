from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_peran
from app.models import Sekolah, Pengguna, PeranPengguna
from app.schemas.sekolah import SekolahDetail, SekolahUpdate
from app.core.responses import EnvelopeAPIRoute


router = APIRouter(
    prefix="/sekolah", tags=["Sekolah"], route_class=EnvelopeAPIRoute
)


@router.get("/profil", response_model=SekolahDetail)
def get_profil_sekolah(
    pengguna: Pengguna = Depends(
        require_peran(
            PeranPengguna.admin_sekolah,
            PeranPengguna.guru,
            PeranPengguna.operator,
            PeranPengguna.keuangan,
        )
    ),
) -> Sekolah:
    sekolah = pengguna.sekolah
    if sekolah is None:
        raise HTTPException(status_code=404, detail="Profil sekolah belum tersedia")
    return sekolah


@router.put("/profil", response_model=SekolahDetail)
def update_profil_sekolah(
    payload: SekolahUpdate,
    db: Session = Depends(get_db),
    pengguna: Pengguna = Depends(require_peran(PeranPengguna.admin_sekolah)),
) -> Sekolah:
    sekolah = pengguna.sekolah
    if sekolah is None:
        raise HTTPException(status_code=404, detail="Profil sekolah belum tersedia")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(sekolah, field, value)

    db.add(sekolah)
    db.commit()
    db.refresh(sekolah)
    return sekolah
