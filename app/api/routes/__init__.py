from fastapi import APIRouter
from . import (
    auth,
    sekolah,
    guru,
    tahun_ajaran,
    mata_pelajaran,
    kelas,
    siswa,
    nilai,
    absensi,
    pembayaran,
    tagihan,
    laporan,
)


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(sekolah.router)
api_router.include_router(guru.router)
api_router.include_router(tahun_ajaran.router)
api_router.include_router(mata_pelajaran.router)
api_router.include_router(kelas.router)
api_router.include_router(siswa.router)
api_router.include_router(nilai.router)
api_router.include_router(absensi.router)
api_router.include_router(pembayaran.router)
api_router.include_router(tagihan.router)
api_router.include_router(laporan.router)
