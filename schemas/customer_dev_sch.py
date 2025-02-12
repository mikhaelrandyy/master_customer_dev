from models.customer_dev_model import CustomerDevBase, CustomerDevFullBase
from schemas.attachment_sch import AttachmentForCustomerDevSch, AttachmentUpdateSch

class CustomerDevCreateSch(CustomerDevBase):
    attachments: list[AttachmentForCustomerDevSch] | None = None

class CustomerDevSch(CustomerDevFullBase):
    pass

class CustomerDevUpdateSch(CustomerDevBase):
    attachments: list[AttachmentUpdateSch] | None = None

class CustomerDevByIdSch(CustomerDevFullBase):
    attachments: list[AttachmentForCustomerDevSch] | None = None


    

