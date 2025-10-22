import uuid
from datetime import datetime
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
