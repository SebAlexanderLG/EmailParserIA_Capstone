from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so


from models.db_model import Base


class Email(Base):
    """Clase Email"""

    __tablename__ = "email"

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    fecha_hora_correo: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    email_id: so.Mapped[int] = so.mapped_column(sa.Text, unique=True, nullable=False)
    remitente_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("remitente.id"), nullable=False
    )
    destinatario_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("usuario.id"), nullable=False
    )
    asunto: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    cuerpo_snippet: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    respuesta_ia: so.Mapped[str | None] = so.mapped_column(sa.Text, nullable=True)
    fecha_envio: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    # Relaciones entre tablas
    remitente: so.Mapped["Remitente"] = so.relationship(
        back_populates="emails_enviados", foreign_keys=[remitente_id]
    )
    destinatario: so.Mapped["Usuario"] = so.relationship(
        "Usuario", back_populates="emails_recibidos", foreign_keys=[destinatario_id]
    )
