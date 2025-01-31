from models.attachment_model import AttachmentBase, AttachmentFullBase
from models.base_model import SQLModel


class AttachmentCreateSch(AttachmentBase):
    pass

class AttachmentSch(AttachmentFullBase):
    pass 

class AttachmentUpdateSch(AttachmentBase):
    id: str | None

class AttachmentByIdSch(AttachmentFullBase):
    pass

class AttachmentForCustomerDevSch(SQLModel):
    doc_type: str | None 
    file_name: str | None 
    file_url: str | None 
    source_process: str | None

