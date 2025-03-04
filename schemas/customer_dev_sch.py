from models.customer_dev_model import CustomerDevBase, CustomerDevFullBase
from schemas.attachment_sch import AttachmentForCustomerDevSch, AttachmentUpdateSch
from sqlmodel import SQLModel

class CustomerDevCreateSch(CustomerDevBase):
    reference_id: str | None = None
    attachments: list[AttachmentForCustomerDevSch] | None = None

class CustomerDevSch(CustomerDevFullBase):
    reference_id: str | None = None

class CustomerDevUpdateSch(CustomerDevBase):
    attachments: list[AttachmentUpdateSch] | None = None

class CustomerDevByIdSch(CustomerDevFullBase):
    reference_id: str | None = None
    attachments: list[AttachmentForCustomerDevSch] | None = None

class ChangeDataSch(SQLModel):
    before: dict
    after: dict
    lastest_source_from: str | None = None
    vs_reference: str 


    

