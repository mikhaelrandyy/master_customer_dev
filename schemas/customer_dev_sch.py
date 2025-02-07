from models.customer_dev_model import CustomerDevBase, CustomerDevFullBase
from schemas.attachment_sch import AttachmentForCustomerDevSch, AttachmentUpdateSch

class CustomerDevCreateSch(CustomerDevBase):
    attachments: list[AttachmentForCustomerDevSch]

class CustomerDevSch(CustomerDevFullBase):
    pass

class CustomerDevUpdateSch(CustomerDevBase):
    attachments: list[AttachmentUpdateSch]

class CustomerDevByIdSch(CustomerDevFullBase):
    attachments: list[AttachmentForCustomerDevSch]


    

