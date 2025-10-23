# Sistem Sekolah Online - Backend FastAPI

## Arsitektur Singkat
- `app/main.py` membuat instance FastAPI dan memuat seluruh router.
- Direktori `app/api/routes` berisi pemetaan endpoint untuk autentikasi, profil sekolah, guru, tahun ajaran, kelas, siswa, nilai, absensi, tagihan, pembayaran, dan laporan.
- Model data terdapat di `app/models` dengan nama kolom menggunakan bahasa Indonesia dan relasi antar entitas yang mencerminkan struktur sekolah di Indonesia.
- Skema Pydantic di `app/schemas` memastikan validasi request/response sesuai konteks domain.
- `app/core` menyimpan konfigurasi aplikasi, keamanan (JWT & hashing kata sandi), serta dependency FastAPI seperti koneksi database dan guard peran.

## Menjalankan Lokal
- Install dependensi: `pip install -r requirements.txt`
- Jalankan migrasi database: `alembic upgrade head`
- Jalankan server dev: `uvicorn app.main:app --reload`

## Alur Utama
- **Registrasi Admin Sekolah**: `POST /auth/register-admin` membuat entitas Sekolah dan Pengguna peran `admin_sekolah`, sekaligus token verifikasi email.
- **Verifikasi Email**: `POST /auth/verifikasi-email` mengesahkan alamat email sebelum login.
- **Login JWT**: `POST /auth/login` mengembalikan token akses untuk admin/guru yang aktif dan terverifikasi.
- **Pengisian Data Sekolah**: Admin mengelola profil melalui `GET/PUT /sekolah/profil`.
- **Manajemen Guru**: Admin menambah, melihat, dan memperbarui guru via `/guru`.
- **Tahun Ajaran & Kelas**: Admin menyusun struktur akademik lewat `/tahun-ajaran` dan `/kelas`.
- **Data Siswa**: Admin menambah dan memindahkan siswa antar kelas lewat `/siswa`.
- **Nilai & Absensi**: Guru maupun admin menginput nilai (`/nilai`) dan absensi (`/absensi`) siswa.
- **Tagihan SPP & Tagihan Lainnya**: Admin/keuangan membuat tagihan bulanan atau khusus serta memantau statusnya via `/tagihan`.
- **Pembayaran**: Admin/keuangan mencatat dan memperbarui transaksi pembayaran `(/pembayaran)` yang otomatis mengupdate tagihan terkait.
- **Laporan Pembayaran**: Rekap tagihan vs pembayaran per bulan/tahun melalui `/laporan/pembayaran`.
- **Website Sekolah**: Admin mengelola berita, pengumuman, dan kegiatan melalui `/website/konten` serta menyediakan endpoint publik `/website/public`.

Semua endpoint daftar (guru, siswa, kelas, mata pelajaran, tahun ajaran, nilai, absensi, tagihan, pembayaran) mendukung query parameter `page` dan `limit` untuk pagination (default `page=1`, `limit=20`).

## Langkah Lanjutan yang Disarankan
1. Integrasi pengiriman email verifikasi (mis. SMTP atau layanan pihak ketiga).
2. Menambah middleware audit trail/log aktivitas penting.
3. Implementasi pagination dan filter lanjutan pada endpoint daftar data.
4. Menambahkan otomasi migrasi database (Alembic) serta seed data awal.
5. Menyusun pengujian unit/integrasi untuk alur kritikal (registrasi, login, CRUD utama).
