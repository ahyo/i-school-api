import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TokenVerifikasiEmail(Base):
    __tablename__ = "token_verifikasi_email"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    pengguna_id: Mapped[str] = mapped_column(
        String, ForeignKey("pengguna.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    kedaluwarsa: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    digunakan: Mapped[bool] = mapped_column(Boolean, default=False)
    pengguna = relationship("Pengguna")


class TokenResetPassword(Base):
    __tablename__ = "token_reset_password"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    pengguna_id: Mapped[str] = mapped_column(
        String, ForeignKey("pengguna.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    kedaluwarsa: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    digunakan: Mapped[bool] = mapped_column(Boolean, default=False)
    pengguna = relationship("Pengguna")


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    pengguna_id: Mapped[str] = mapped_column(
        String, ForeignKey("pengguna.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    kedaluwarsa: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dicabut: Mapped[bool] = mapped_column(Boolean, default=False)
    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    pengguna = relationship("Pengguna")
