import sqlalchemy as sa
import sqlalchemy.orm as so

from models.db_model import Base


class Email(Base):
    """Clase Email"""

    __tablename__ = "emails"

    id: so.Mapped[int] = so.MappedColumn(
        sa.Integer, primary_key=True, autoincrement=True
    )
