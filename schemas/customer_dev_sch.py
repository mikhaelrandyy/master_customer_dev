from models.customer_dev_model import CustomerDevBase, CustomerDevFullBase
from schemas.attachment_sch import AttachmentForCustomerDevSch


class CustomerDevCreateSch(CustomerDevBase):
    attachments: list[AttachmentForCustomerDevSch]

class CustomerDevSch(CustomerDevFullBase):
    attachments: list[AttachmentForCustomerDevSch]

class CustomerDevUpdateSch(CustomerDevBase):
    id: str

class CustomerDevByIdSch(CustomerDevFullBase):
    pass

