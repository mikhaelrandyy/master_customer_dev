from ulid import ULID
from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING

from models.base_model import BaseULIDModel, SQLModel

if TYPE_CHECKING:
    from models import CustomerDev


class AttachmentBase(SQLModel):
    customer_id: str | None = Field(nullable=True, foreign_key="customer_dev.id")
    doc_type: str | None = Field(nullable=True)
    file_name: str | None = Field(nullable=True)
    file_url: str | None = Field(nullable=True)
    source_process: str = Field(nullable=False) #UPDATE APLIKASI FROM
    is_active: bool | None = Field(nullable=True)

class AttachmentFullBase(AttachmentBase, BaseULIDModel):
    pass

class Attachment(AttachmentFullBase, table=True):
    customer_dev: "CustomerDev" = Relationship(
        sa_relationship_kwargs = {
            "lazy": "select"
        }
    )