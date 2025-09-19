import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class Remitente(Base):
    """Clase Remitente"""

    __tablename__ = "remitentes"

    id: so.Mapped[int] = so.MappedColumn(
        sa.Integer, primary_key=True, autoincrement=True
    )
    usuario_id: so.Mapped[int] = so.MappedColumn(
        sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False, index=True
    )
    nombre_remitente: so.Mapped[str] = so.mapped_column(
        sa.String(50), nullable=False, index=True
    )
    nombre_correo: so.Mapped[str] = so.MappedColumn(
        sa.String(100), nullable=False, index=True
    )
    tipo_correo: so.Mapped[str] = so.MappedColumn(
        sa.String(50), nullable=False, index=True
    )
