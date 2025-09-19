import sqlalchemy as sa


class EstadoEmailEnum(sa.Enum):
    LEIDO = "Leído"
    NO_LEIDO = "No Leído"
