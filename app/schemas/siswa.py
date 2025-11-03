from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.referensi import JenisKelamin
from app.models.siswa import StatusSiswa, StatusKeanggotaanKelas
from app.models.pembayaran import (
    JenisPembayaran,
    StatusPembayaran,
    StatusTagihan,
)
from app.models.akademik import Semester, TipePenilaian, StatusKehadiran


class SiswaBase(BaseModel):
    nisn: str | None = Field(default=None, max_length=20)
    nis: str | None = Field(default=None, max_length=20)
    nama_lengkap: str = Field(..., max_length=150)
    nama_panggilan: str | None = Field(default=None, max_length=50)
    jenis_kelamin: JenisKelamin
    tempat_lahir: str | None = Field(default=None, max_length=100)
    tanggal_lahir: date | None = None
    agama: str | None = Field(default=None, max_length=50)
    alamat: str | None = Field(default=None, max_length=255)
    nomor_telepon: str | None = Field(default=None, max_length=25)
    nama_ayah: str | None = Field(default=None, max_length=150)
    nama_ibu: str | None = Field(default=None, max_length=150)
    wali_murid: str | None = Field(default=None, max_length=150)
    status_siswa: StatusSiswa = StatusSiswa.aktif
    tanggal_diterima: date | None = None
    catatan: str | None = Field(default=None, max_length=500)


class SiswaCreate(SiswaBase):
    kelas_id: str | None = None


class SiswaUpdate(BaseModel):
    nisn: str | None = Field(default=None, max_length=20)
    nis: str | None = Field(default=None, max_length=20)
    nama_lengkap: str | None = Field(default=None, max_length=150)
    nama_panggilan: str | None = Field(default=None, max_length=50)
    jenis_kelamin: JenisKelamin | None = None
    tempat_lahir: str | None = Field(default=None, max_length=100)
    tanggal_lahir: date | None = None
    agama: str | None = Field(default=None, max_length=50)
    alamat: str | None = Field(default=None, max_length=255)
    nomor_telepon: str | None = Field(default=None, max_length=25)
    nama_ayah: str | None = Field(default=None, max_length=150)
    nama_ibu: str | None = Field(default=None, max_length=150)
    wali_murid: str | None = Field(default=None, max_length=150)
    status_siswa: StatusSiswa | None = None
    tanggal_diterima: date | None = None
    catatan: str | None = Field(default=None, max_length=500)
    kelas_id: str | None = None


class KelasRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_kelas: str
    tingkat: int
    rombel: str | None = None


class SiswaKelasRiwayat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    siswa_id: str
    kelas_id: str
    status_keanggotaan: StatusKeanggotaanKelas
    tanggal_masuk: date | None = None
    tanggal_keluar: date | None = None
    kelas: KelasRingkas


class TagihanRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    jenis_tagihan: JenisPembayaran
    nama_tagihan: str
    jumlah_tagihan: Decimal
    jumlah_terbayar: Decimal
    status_tagihan: StatusTagihan
    tanggal_jatuh_tempo: date | None = None


class PembayaranRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tagihan_id: str | None = None
    jenis_pembayaran: JenisPembayaran
    jumlah: Decimal
    status_pembayaran: StatusPembayaran
    tanggal_bayar: date | None = None


class NilaiRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mata_pelajaran_id: str
    kelas_id: str | None = None
    tahun_ajaran_id: str
    semester: Semester
    tipe_penilaian: TipePenilaian
    nilai_angka: Decimal | None = None
    nilai_huruf: str | None = None
    tanggal_penilaian: date | None = None


class AbsensiRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kelas_id: str | None = None
    mata_pelajaran_id: str | None = None
    tanggal: date
    status_kehadiran: StatusKehadiran
    keterangan: str | None = None


class SiswaDetail(SiswaBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sekolah_id: str
    dibuat_pada: datetime
    diperbarui_pada: datetime
    riwayat_kelas: list[SiswaKelasRiwayat] = Field(default_factory=list)
    tagihan: list[TagihanRingkas] = Field(default_factory=list)
    pembayaran: list[PembayaranRingkas] = Field(default_factory=list)
    nilai: list[NilaiRingkas] = Field(default_factory=list)
    absensi: list[AbsensiRingkas] = Field(default_factory=list)


class SiswaRingkas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama_lengkap: str
    nisn: str | None = None
