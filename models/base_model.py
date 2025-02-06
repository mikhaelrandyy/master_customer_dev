from datetime import datetime
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel as _SQLModel, Field
from stringcase import snakecase
from ulid import ULID

class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return snakecase(cls.__name__)
    
    
def generate_ulid() -> str:
    return str(ULID())

class BaseFieldULIDModel(SQLModel):
    id: str | None = Field(
        default_factory=generate_ulid, 
        primary_key=True, 
        index=True, 
        nullable=False, 
        max_length=26
    )
    
class BaseULIDModel(BaseFieldULIDModel):
    created_by: str = Field(nullable=False, default="admin")
    updated_by: str = Field(nullable=False, default="admin")
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)