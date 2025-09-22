from __future__ import annotations
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class GmailToken(Base):
    __tablename__ = "token"

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )

    # Clave foranea hacia clase "Usuario"
    usuario_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("usuario.id"), nullable=False
    )

    access_token: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    refresh_token: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    token_type: so.Mapped[str] = so.mapped_column(sa.Text, default="Bearer")
    scope: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    expires_in: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    refresh_token_expires_in: so.Mapped[int] = so.mapped_column(
        sa.Integer, nullable=True
    )
    expires_at: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    usuario: so.Mapped["Usuario"] = so.relationship("Usuario", back_populates="token")
