from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class Prompt(Base):
    """Clase Prompt"""

    __tablename__ = "prompt"

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    fecha_creacion: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    contexto: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    remitente_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey("remitente.id"), nullable=False, unique=True
    )

    # Relación con Remitente
    remitente: so.Mapped["Remitente"] = so.relationship(
        "Remitente", back_populates="prompt"
    )
