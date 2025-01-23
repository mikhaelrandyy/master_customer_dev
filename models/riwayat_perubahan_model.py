from ulid import ULID
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from models.base_model import BaseULIDModel, SQLModel
from models import CustomerDev


class RiwayatPerubahanBase(SQLModel):
    reference_id: str = Field(nullable=False)
    before: dict = Field(sa_type=JSONB, nullable=True) #TIPE DATANYA JSON
    after: dict = Field(sa_type=JSONB, nullable=True)
    source_process: str = Field(nullable=False)  #UPDATE APLIKASI FROM
    source_table: str = Field(nullable=False)

class RiwayatPerubahanFullBase(RiwayatPerubahanBase, BaseULIDModel):
    pass


class RiwayatPerubahan(RiwayatPerubahanFullBase, table=True):
    customer_dev: "CustomerDev" = Relationship(
        sa_relationship_kwargs = {
            "lazy": "select"
        }
    )