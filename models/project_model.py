from models.base_model import BaseULIDModel
from sqlmodel import SQLModel, Field

class ProjectBase(SQLModel):
    code: str = Field(nullable=False, max_length=50)
    name: str = Field(nullable=False, max_length=100)

class ProjectFullBase(BaseULIDModel, ProjectBase):
    pass

class Project(ProjectFullBase, table=True):
    pass