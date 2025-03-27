from ulid import ULID
from sqlmodel import Field

from models.base_model import SQLModel


class CustomerDevGroupBase(SQLModel):
    customer_parent_id: str | None = Field(nullable=False, primary_key=True, foreign_key="customer_dev.id")
    customer_reference_id: str | None = Field(nullable=False, primary_key=True, foreign_key="customer_dev.id")

class CustomerDevGroup(CustomerDevGroupBase, table=True):
    pass