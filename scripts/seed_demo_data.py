"""Seed demo data for Sistem Sekolah Online.

This script will insert a default school, admin user, and sample website content
so the frontend can display meaningful data on first run.
"""

from datetime import datetime, timezone, date
from pathlib import Path
import sys

from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.security import buat_hash_kata_sandi
from app.db.session import SessionLocal
from app.models import (
    JenisKonten,
    JenjangSekolah,
    PeranPengguna,
    Sekolah,
    StatusKonten,
    StatusSekolah,
    WebsiteKonten,
    Pengguna,
)
from app.models.guru import Guru, StatusGuru
from app.models.mata_pelajaran import (
    KelompokMataPelajaran,
    MataPelajaran,
)
from app.models.akademik import (
    TahunAjaran,
    Semester,
    Kelas,
    GuruMataPelajaran,
    AbsensiSiswa,
    StatusKehadiran,
    Nilai,
    TipePenilaian,
    KenaikanKelas,
    StatusKenaikan,
)
from app.models.referensi import JenisKelamin
from app.models.siswa import (
    Siswa,
    StatusSiswa,
    SiswaKelas,
    StatusKeanggotaanKelas,
)
from app.models.catatan import CatatanSiswa, KategoriCatatan


DEMO_SEKOLAH_NAMA = "SMA Negeri Teladan"
DEMO_ADMIN_EMAIL = "admin@sma-teladan.sch.id"
DEMO_ADMIN_PASSWORD = "P@ssw0rd!"


def get_or_create_demo_sekolah(session: Session) -> Sekolah:
    sekolah = (
        session.query(Sekolah)
        .filter(Sekolah.nama_sekolah == DEMO_SEKOLAH_NAMA)
        .first()
    )
    if sekolah:
        return sekolah

    sekolah = Sekolah(
        nama_sekolah=DEMO_SEKOLAH_NAMA,
        jenjang=JenjangSekolah.sma,
        status=StatusSekolah.negeri,
        alamat_jalan="Jl. Pendidikan No. 123",
        kelurahan="Mentari",
        kecamatan="Cendekia",
        kota_kabupaten="Kota Inspirasi",
        provinsi="Jawa Barat",
        kode_pos="40123",
        nomor_telepon="021-1234567",
        email_resmi="info@sma-teladan.sch.id",
        website="https://sma-teladan.sch.id",
        kepala_sekolah="Drs. Agus Pratama",
        status_verifikasi=True,
        deskripsi=(
            "Sekolah unggulan dengan fokus pada pengembangan karakter "
            "dan prestasi akademik maupun non-akademik."
        ),
    )
    session.add(sekolah)
    session.flush()
    return sekolah


def get_or_create_demo_admin(session: Session, sekolah: Sekolah) -> Pengguna:
    admin = (
        session.query(Pengguna)
        .filter(Pengguna.email == DEMO_ADMIN_EMAIL)
        .first()
    )
    if admin:
        return admin

    admin = Pengguna(
        nama_lengkap="Admin Demo",
        email=DEMO_ADMIN_EMAIL,
        kata_sandi_hash=buat_hash_kata_sandi(DEMO_ADMIN_PASSWORD),
        peran=PeranPengguna.admin_sekolah,
        email_terverifikasi=True,
        status_aktif=True,
        sekolah_id=sekolah.id,
    )
    session.add(admin)
    session.flush()
    return admin


def get_or_create_tahun_ajaran(session: Session, sekolah: Sekolah) -> TahunAjaran:
    tahun = (
        session.query(TahunAjaran)
        .filter(
            TahunAjaran.sekolah_id == sekolah.id,
            TahunAjaran.aktif.is_(True),
        )
        .first()
    )
    if tahun:
        return tahun

    tahun = TahunAjaran(
        sekolah_id=sekolah.id,
        nama_tahun="2024/2025",
        tanggal_mulai=datetime(2024, 7, 15, tzinfo=timezone.utc).date(),
        tanggal_selesai=datetime(2025, 6, 30, tzinfo=timezone.utc).date(),
        semester_awal=Semester.ganjil,
        aktif=True,
    )
    session.add(tahun)
    session.flush()
    return tahun


def ensure_mata_pelajaran(session: Session, sekolah: Sekolah) -> list[MataPelajaran]:
    existing = (
        session.query(MataPelajaran)
        .filter(MataPelajaran.sekolah_id == sekolah.id)
        .all()
    )
    if existing:
        return existing

    mapel_data = [
        ("MAT", "Matematika", KelompokMataPelajaran.umum),
        ("BIO", "Biologi", KelompokMataPelajaran.umum),
        ("BIND", "Bahasa Indonesia", KelompokMataPelajaran.umum),
        ("BING", "Bahasa Inggris", KelompokMataPelajaran.umum),
    ]
    created: list[MataPelajaran] = []
    for kode, nama, kelompok in mapel_data:
        mapel = MataPelajaran(
            sekolah_id=sekolah.id,
            kode_mapel=kode,
            nama_mapel=nama,
            kelompok=kelompok,
            tingkat_minimal=10,
            tingkat_maksimal=12,
            status_aktif=True,
        )
        session.add(mapel)
        created.append(mapel)
    session.flush()
    return created


def ensure_guru(
    session: Session,
    sekolah: Sekolah,
    mata_pelajaran: list[MataPelajaran],
) -> list[Guru]:
    guru_emails = [
        "ratna@sma-teladan.sch.id",
        "budi@sma-teladan.sch.id",
        "dina@sma-teladan.sch.id",
    ]
    existing = (
        session.query(Guru)
        .join(Pengguna)
        .filter(Guru.sekolah_id == sekolah.id, Pengguna.email.in_(guru_emails))
        .all()
    )
    if len(existing) == len(guru_emails):
        return existing

    guru_data = [
        {
            "nama": "Ratna Puspitasari",
            "email": guru_emails[0],
            "kelamin": JenisKelamin.perempuan,
            "mapel": "Matematika",
        },
        {
            "nama": "Budi Hartono",
            "email": guru_emails[1],
            "kelamin": JenisKelamin.laki_laki,
            "mapel": "Biologi",
        },
        {
            "nama": "Dina Larasati",
            "email": guru_emails[2],
            "kelamin": JenisKelamin.perempuan,
            "mapel": "Bahasa Inggris",
        },
    ]
    mapel_lookup = {m.nama_mapel: m for m in mata_pelajaran}
    created: list[Guru] = []
    for data in guru_data:
        pengguna = (
            session.query(Pengguna)
            .filter(Pengguna.email == data["email"])
            .first()
        )
        if pengguna is None:
            pengguna = Pengguna(
                nama_lengkap=data["nama"],
                email=data["email"],
                kata_sandi_hash=buat_hash_kata_sandi("GuruTeladan123"),
                peran=PeranPengguna.guru,
                sekolah_id=sekolah.id,
                email_terverifikasi=True,
                status_aktif=True,
            )
            session.add(pengguna)
            session.flush()
        guru = (
            session.query(Guru)
            .filter(Guru.pengguna_id == pengguna.id)
            .first()
        )
        if guru is None:
            guru = Guru(
                pengguna_id=pengguna.id,
                sekolah_id=sekolah.id,
                jenis_kelamin=data["kelamin"],
                mata_pelajaran_utama=data["mapel"],
                status_guru=StatusGuru.aktif,
            )
            session.add(guru)
            session.flush()

        mapel_name = data["mapel"]
        mapel = mapel_lookup.get(mapel_name)
        if mapel:
            relasi = (
                session.query(GuruMataPelajaran)
                .filter(
                    GuruMataPelajaran.guru_id == guru.id,
                    GuruMataPelajaran.mata_pelajaran_id == mapel.id,
                )
                .first()
            )
            if relasi is None:
                session.add(
                    GuruMataPelajaran(
                        guru_id=guru.id,
                        mata_pelajaran_id=mapel.id,
                    )
                )

        created.append(guru)
    session.flush()
    return created


def ensure_kelas(
    session: Session,
    sekolah: Sekolah,
    tahun_ajaran: TahunAjaran,
    guru_list: list[Guru],
) -> list[Kelas]:
    existing = (
        session.query(Kelas)
        .filter(Kelas.sekolah_id == sekolah.id)
        .all()
    )
    if existing:
        return existing

    kelas_data = [
        ("X IPA 1", 10, "A", "IPA", guru_list[0].id),
        ("XI IPA 1", 11, "A", "IPA", guru_list[1].id),
        ("XII Bahasa 1", 12, "A", "Bahasa", guru_list[2].id),
    ]
    created: list[Kelas] = []
    for nama, tingkat, rombel, jurusan, wali_id in kelas_data:
        kelas = Kelas(
            sekolah_id=sekolah.id,
            tahun_ajaran_id=tahun_ajaran.id,
            nama_kelas=nama,
            tingkat=tingkat,
            rombel=rombel,
            jurusan=jurusan,
            wali_kelas_id=wali_id,
            kapasitas=32,
        )
        session.add(kelas)
        created.append(kelas)
    session.flush()
    return created


def ensure_siswa(
    session: Session,
    sekolah: Sekolah,
    kelas_list: list[Kelas],
) -> list[Siswa]:
    existing = (
        session.query(Siswa)
        .filter(Siswa.sekolah_id == sekolah.id)
        .all()
    )
    if existing:
        return existing

    siswa_data = [
        {
            "nama": "Andi Nugroho",
            "kelas": kelas_list[0],
            "kelamin": JenisKelamin.laki_laki,
            "tanggal_lahir": date(2008, 4, 5),
        },
        {
            "nama": "Siti Rahmawati",
            "kelas": kelas_list[0],
            "kelamin": JenisKelamin.perempuan,
            "tanggal_lahir": date(2008, 9, 12),
        },
        {
            "nama": "Bagus Wiratama",
            "kelas": kelas_list[1],
            "kelamin": JenisKelamin.laki_laki,
            "tanggal_lahir": date(2007, 2, 18),
        },
    ]
    created: list[Siswa] = []
    for index, data in enumerate(siswa_data, start=1):
        siswa = Siswa(
            sekolah_id=sekolah.id,
            nisn=f"20240{index:03d}",
            nis=f"10{index:03d}",
            nama_lengkap=data["nama"],
            jenis_kelamin=data["kelamin"],
            tanggal_lahir=data["tanggal_lahir"],
            status_siswa=StatusSiswa.aktif,
            tanggal_diterima=date(2024, 7, 15),
        )
        session.add(siswa)
        session.flush()

        relasi = SiswaKelas(
            siswa_id=siswa.id,
            kelas_id=data["kelas"].id,
            status_keanggotaan=StatusKeanggotaanKelas.aktif,
            tanggal_masuk=date(2024, 7, 15),
        )
        session.add(relasi)
        created.append(siswa)

    session.flush()
    return created


def ensure_absensi(
    session: Session,
    sekolah: Sekolah,
    siswa_list: list[Siswa],
    kelas_list: list[Kelas],
    mapel_list: list[MataPelajaran],
) -> None:
    existing = (
        session.query(AbsensiSiswa)
        .filter(AbsensiSiswa.sekolah_id == sekolah.id)
        .first()
    )
    if existing:
        return

    records = [
        {
            "siswa": siswa_list[0],
            "kelas": kelas_list[0],
            "mapel": mapel_list[0],
            "status": StatusKehadiran.hadir,
            "tanggal": date(2024, 8, 1),
        },
        {
            "siswa": siswa_list[1],
            "kelas": kelas_list[0],
            "mapel": mapel_list[0],
            "status": StatusKehadiran.sakit,
            "tanggal": date(2024, 8, 1),
            "keterangan": "Sakit flu",
        },
        {
            "siswa": siswa_list[2],
            "kelas": kelas_list[1],
            "mapel": mapel_list[1],
            "status": StatusKehadiran.hadir,
            "tanggal": date(2024, 8, 1),
        },
    ]
    for item in records:
        session.add(
            AbsensiSiswa(
                sekolah_id=sekolah.id,
                siswa_id=item["siswa"].id,
                kelas_id=item["kelas"].id,
                mata_pelajaran_id=item["mapel"].id,
                tanggal=item["tanggal"],
                status_kehadiran=item["status"],
                keterangan=item.get("keterangan"),
            )
        )


def ensure_nilai(
    session: Session,
    sekolah: Sekolah,
    siswa_list: list[Siswa],
    kelas_list: list[Kelas],
    mapel_list: list[MataPelajaran],
    tahun: TahunAjaran,
) -> None:
    existing = (
        session.query(Nilai)
        .filter(Nilai.sekolah_id == sekolah.id)
        .first()
    )
    if existing:
        return

    guru = (
        session.query(Guru)
        .filter(Guru.sekolah_id == sekolah.id)
        .first()
    )
    for siswa in siswa_list:
        session.add(
            Nilai(
                sekolah_id=sekolah.id,
                siswa_id=siswa.id,
                kelas_id=kelas_list[0].id if kelas_list else None,
                mata_pelajaran_id=mapel_list[0].id,
                guru_id=guru.id if guru else None,
                tahun_ajaran_id=tahun.id,
                semester=Semester.ganjil,
                tipe_penilaian=TipePenilaian.pengetahuan,
                nilai_angka=88,
                nilai_huruf="A",
                deskripsi="Ulangan harian materi fungsi kuadrat.",
                tanggal_penilaian=date(2024, 9, 10),
            )
        )
        session.add(
            Nilai(
                sekolah_id=sekolah.id,
                siswa_id=siswa.id,
                kelas_id=kelas_list[0].id if kelas_list else None,
                mata_pelajaran_id=mapel_list[0].id,
                guru_id=guru.id if guru else None,
                tahun_ajaran_id=tahun.id,
                semester=Semester.ganjil,
                tipe_penilaian=TipePenilaian.uts,
                nilai_angka=82,
                nilai_huruf="B+",
                deskripsi="Ujian Tengah Semester Ganjil.",
                tanggal_penilaian=date(2024, 10, 20),
            )
        )
        session.add(
            Nilai(
                sekolah_id=sekolah.id,
                siswa_id=siswa.id,
                kelas_id=kelas_list[0].id if kelas_list else None,
                mata_pelajaran_id=mapel_list[0].id,
                guru_id=guru.id if guru else None,
                tahun_ajaran_id=tahun.id,
                semester=Semester.genap,
                tipe_penilaian=TipePenilaian.uas,
                nilai_angka=90,
                nilai_huruf="A",
                deskripsi="Ujian Akhir Semester Genap.",
                tanggal_penilaian=date(2025, 4, 5),
            )
        )


def ensure_kenaikan(
    session: Session,
    sekolah: Sekolah,
    siswa_list: list[Siswa],
    kelas_list: list[Kelas],
    tahun: TahunAjaran,
) -> None:
    existing = (
        session.query(KenaikanKelas)
        .join(Siswa)
        .filter(Siswa.sekolah_id == sekolah.id)
        .first()
    )
    if existing:
        return

    for siswa in siswa_list:
        session.add(
            KenaikanKelas(
                siswa_id=siswa.id,
                kelas_asal_id=kelas_list[0].id if kelas_list else None,
                kelas_tujuan_id=kelas_list[1].id if len(kelas_list) > 1 else None,
                tahun_ajaran_asal_id=tahun.id,
                tahun_ajaran_tujuan_id=tahun.id,
                status_kenaikan=StatusKenaikan.naik,
                tanggal_keputusan=date(2025, 6, 20),
                catatan="Siswa memenuhi seluruh kriteria kenaikan kelas.",
            )
        )


def ensure_catatan(
    session: Session,
    sekolah: Sekolah,
    siswa_list: list[Siswa],
    pencatat: Pengguna,
) -> None:
    existing = (
        session.query(CatatanSiswa)
        .filter(CatatanSiswa.sekolah_id == sekolah.id)
        .first()
    )
    if existing or not siswa_list:
        return

    session.add(
        CatatanSiswa(
            sekolah_id=sekolah.id,
            siswa_id=siswa_list[0].id,
            kategori=KategoriCatatan.akademik,
            judul="Perkembangan Akademik",
            isi=(
                "Siswa menunjukkan peningkatan signifikan pada materi matematika."
                " Tetap perlu pendampingan dalam tugas rumah."
            ),
            pencatat_id=pencatat.id if pencatat else None,
        )
    )


def ensure_sample_content(session: Session, sekolah: Sekolah) -> None:
    existing = (
        session.query(WebsiteKonten)
        .filter(WebsiteKonten.sekolah_id == sekolah.id)
        .first()
    )
    if existing:
        return

    artikel = WebsiteKonten(
        sekolah_id=sekolah.id,
        penulis_id=None,
        judul="Penerimaan Peserta Didik Baru Telah Dibuka",
        slug="penerimaan-peserta-didik-baru",
        jenis=JenisKonten.pengumuman,
        status=StatusKonten.terbit,
        ringkasan=(
            "SMA Negeri Teladan resmi membuka pendaftaran siswa baru tahun ajaran 2024/2025."
        ),
        isi=(
            "Pendaftaran siswa baru telah dibuka! Calon peserta didik dapat melakukan "
            "pendaftaran secara daring melalui formulir yang tersedia di website. "
            "Informasi lebih lanjut terkait persyaratan dan jadwal seleksi dapat "
            "diperoleh melalui kontak resmi sekolah."
        ),
        banner_url="https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1200&q=80",
        tanggal_terbit=datetime.now(timezone.utc),
        tag_meta="ppdb, pendaftaran, berita sekolah",
    )
    session.add(artikel)


def main() -> None:
    with SessionLocal() as session:
        sekolah = get_or_create_demo_sekolah(session)
        admin = get_or_create_demo_admin(session, sekolah)
        tahun = get_or_create_tahun_ajaran(session, sekolah)
        mapel = ensure_mata_pelajaran(session, sekolah)
        guru = ensure_guru(session, sekolah, mapel)
        kelas = ensure_kelas(session, sekolah, tahun, guru)
        siswa = ensure_siswa(session, sekolah, kelas)
        ensure_absensi(session, sekolah, siswa, kelas, mapel)
        ensure_nilai(session, sekolah, siswa, kelas, mapel, tahun)
        ensure_kenaikan(session, sekolah, siswa, kelas, tahun)
        pencatat = guru[0].pengguna if guru and guru[0].pengguna else admin
        ensure_catatan(session, sekolah, siswa, pencatat)
        ensure_sample_content(session, sekolah)
        session.commit()
        print("Demo data berhasil dibuat.")
        print(f"  Sekolah : {sekolah.nama_sekolah} (ID: {sekolah.id})")
        print(f"  Admin   : {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}")
        if guru:
            print("  Guru    :")
            for g in guru:
                print(
                    f"    - {g.pengguna.nama_lengkap} ({g.pengguna.email}) / GuruTeladan123"
                )
        print("  Kelas   :")
        for kls in kelas:
            print(f"    - {kls.nama_kelas} (Tingkat {kls.tingkat})")
        print("  Siswa   :")
        for sis in siswa:
            print(f"    - {sis.nama_lengkap} ({sis.nisn})")


if __name__ == "__main__":
    main()
