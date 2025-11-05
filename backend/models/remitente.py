import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base
from models.email import Email
from models.usuario import Usuario


class Remitente(Base):
    """Clase Remitente"""

    __tablename__ = "remitente"

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    usuario_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("usuario.id"), nullable=False, index=True
    )
    nombre_correo: so.Mapped[str] = so.mapped_column(
        sa.Text, nullable=False, index=True
    )
    nombre_remitente: so.Mapped[str | None] = so.mapped_column(
        sa.Text, nullable=True, index=True
    )

    # Relaciones entre tablas
    usuario: so.Mapped["Usuario"] = so.relationship(
        "Usuario", back_populates="remitentes"
    )
    emails_enviados: so.Mapped[list["Email"]] = so.relationship(
        "Email", back_populates="remitente", foreign_keys="Email.remitente_id"
    )
