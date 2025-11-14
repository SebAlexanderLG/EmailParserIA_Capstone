from __future__ import annotations
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class Usuario(Base):
    """Clase Usuario"""

    __tablename__ = "usuario"

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    nombre_usuario: so.Mapped[str] = so.mapped_column(
        sa.Text, nullable=False, index=True, unique=True
    )
    email: so.Mapped[str] = so.mapped_column(
        sa.Text, nullable=False, index=True, unique=True
    )
    oauth_access_token: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    oauth_refresh_token: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    ultima_sesion: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    # Relacion con tablas
    remitentes: so.Mapped["Remitente"] = so.relationship(
        "Remitente", back_populates="usuario", uselist=False
    )
    gmail_token: so.Mapped["GmailToken"] = so.relationship(
        "GmailToken", back_populates="usuario", uselist=False
    )
    emails_recibidos: so.Mapped[list["Email"]] = so.relationship(
        "Email", back_populates="destinatario"
    )
    prompts: so.Mapped[list["Prompt"]] = so.relationship(
        "Prompt", back_populates="usuario"
    )
