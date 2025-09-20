from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class EnvioCorreoDocente(Base):
    __tablename__ = "envio_correo_docente"
    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    email_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("email.id"), nullable=False
    )
    remitente_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("remitente.id"), nullable=False
    )
    fecha_envio: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    # Relaciones con tablas
    email: so.Mapped["Email"] = so.relationship(
        "Email", back_populates="accion_envio_correo"
    )
    remitente: so.Mapped["Remitente"] = so.relationship(
        "Remitente", back_populates="accion_envio_correo"
    )
