from ulid import ULID
from sqlmodel import Field, Relationship

from models.base_model import BaseULIDModel, SQLModel
from models import CustomerDev


class CustomerDevGroupBase(SQLModel):
    customer_parent_id: str | None = Field(nullable=True, foreign_key="customer_dev.id")
    customer_reference_id: str | None = Field(nullable=True, foreign_key="customer_dev.id")

class CustomerDevGroupFullBase(CustomerDevGroupBase, BaseULIDModel):
    pass

class CustomerDevGroup(CustomerDevGroupFullBase, table=True):
    pass