from ulid import ULID
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from models.base_model import BaseULIDModel, SQLModel
from models import CustomerDev


class HistoryLogBase(SQLModel):
    reference_id: str = Field(nullable=False)
    before: dict = Field(sa_type=JSONB, nullable=True) #TIPE DATANYA JSON
    after: dict = Field(sa_type=JSONB, nullable=True)
    source_process: str = Field(nullable=False)  #UPDATE APLIKASI FROM
    source_table: str = Field(nullable=False)

class HistoryLogFullBase(HistoryLogBase, BaseULIDModel):
    pass


class HistoryLog(HistoryLogFullBase, table=True):
    pass