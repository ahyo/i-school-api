from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Mengimpor model agar metadata terdaftar saat aplikasi dimuat.
from app import models  # noqa: E402,F401
