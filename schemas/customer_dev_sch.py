from models.customer_dev_model import CustomerDevBase, CustomerDevFullBase
from schemas.attachment_sch import AttachmentForCustomerDevSch, AttachmentUpdateSch

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


    

