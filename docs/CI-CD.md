# CI/CD ke Alibaba Cloud ECS

Workflow GitHub Actions `.github/workflows/deploy.yml` mengotomatisasi:

1. Install dependensi backend dengan `pip install -r requirements.txt` dan menjalankan `python -m compileall app` sebagai smoke-test sintaks.
2. Build image Docker dan push ke **Alibaba Cloud Container Registry (ACR)** dengan tag `github.sha`.
3. Export `requirements.txt`, sinkronisasi kode ke instance **Alibaba Cloud Elastic Compute Service (ECS)** dengan `rsync`, membuat virtualenv dan menginstal dependensi, lalu menjalankan ulang service (atau fallback ke `uvicorn` background process).

## Konfigurasi GitHub Actions

### Secrets
Tambahkan melalui **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Keterangan |
| ------ | ---------- |
| `ECS_SSH_KEY` | Private key SSH (format PEM) yang dipakai untuk mengakses instance ECS. Pastikan public key-nya sudah ditambahkan ke server. |
| `SECRET_KEY` | Nilai `secret_key` untuk konfigurasi aplikasi. |
| `DATABASE_URL` | URL koneksi database PostgreSQL. |
| `EMAIL_SENDER` | Email default pengirim notifikasi. |
| `EMAIL_SENDER_NAME` | (Opsional) Nama pengirim email. |
| `BASE_URL` | (Opsional) Basis URL aplikasi untuk tautan publik. |
| `TIMEZONE` | (Opsional) Zona waktu default, mis. `Asia/Jakarta`. |

### Variables
Tambahkan melalui **Settings → Secrets and variables → Actions → Variables**:

| Variable | Contoh Nilai | Deskripsi |
| -------- | ------------- | --------- |
| `ECS_HOST` | `47.xxx.xxx.xxx` | IP publik atau hostname instance ECS. |
| `ECS_USER` | `ecs-user` | User SSH yang digunakan untuk deploy. |
| `ECS_SSH_PORT` | `22` *(opsional)* | Port SSH jika berbeda dari default. |
| `REMOTE_PATH` | `/home/ecs-user/sistem-sekolah.online/backend` | Direktori project di server ECS. |
| `RESTART_COMMAND` | `systemctl --user restart si-sekolah-backend.service` *(opsional)* | Perintah untuk me-restart service setelah deployment. Jika kosong, workflow menjalankan `uvicorn` secara background. |

## Persiapan di Alibaba Cloud
1. **Python 3.11** terpasang di ECS (cek dengan `python3 --version`).
2. Pastikan folder target (`REMOTE_PATH`) bisa diakses oleh user SSH dan memiliki izin tulis.
3. Simpan file `.env` di server (mis. `/home/ecs-user/sistem-sekolah.online/backend/.env`) dan jangan ditrack di repository.
4. (Opsional) Buat service/systemd atau supervisor yang menjalankan `uvicorn app.main:app` memakai virtualenv `.venv` di folder project. Gunakan `RESTART_COMMAND` untuk memicu restart.

## Apa yang Dilakukan di Server
Langkah SSH dalam workflow menjalankan skrip berikut:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
.venv/bin/alembic upgrade head
<RESTART_COMMAND atau fallback uvicorn background>
```

Jika `RESTART_COMMAND` tidak diisi, workflow otomatis mematikan proses `uvicorn` lama dan menjalankan ulang dengan:

```bash
pkill -f "uvicorn app.main:app" || true
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

## Menjalankan Workflow
- **Push ke `main`** otomatis memicu proses build dan deploy.
- **Pull Request ke `main`** hanya menjalankan job build/test tanpa deploy.
- Anda juga dapat menjalankan manual via **Actions → CI/CD Alibaba ECS → Run workflow**.
