from sqlalchemy.orm import DeclarativeBase

# Mengimpor model agar metadata terdaftar saat aplikasi dimuat.
from app import models  # noqa: F401


class Base(DeclarativeBase):
    pass
