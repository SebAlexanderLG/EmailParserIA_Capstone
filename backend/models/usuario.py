from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class Usuario(Base):
    """Clase Usuario"""

    __tablename__ = "usuarios"

    id: so.Mapped[int] = so.MappedColumn(
        sa.Integer, primary_key=True, autoincrement=True
    )
    nombre_usuario: so.Mapped[str] = so.MappedColumn(
        sa.String(50), nullable=False, index=True, unique=True
    )
    email: so.Mapped[str] = so.MappedColumn(
        sa.String(100), nullable=False, index=True, unique=True
    )
    oauth_access_token: so.Mapped[str] = so.MappedColumn(
        sa.String(255), nullable=False, index=True
    )
    oauth_refresh_token: so.Mapped[str] = so.MappedColumn(
        sa.String(512), nullable=False, index=True
    )
    ultima_sesion: so.Mapped[datetime] = so.MappedColumn(
        sa.DateTime(timezone=True), nullable=True, index=True
    )
