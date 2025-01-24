from models.customer_dev_model import CustomerDevBase, CustomerDevFullBase


class CustomerDevCreateSch(CustomerDevBase):
    pass

class CustomerDevSch(CustomerDevFullBase):
    pass 

class CustomerDevUpdateSch(CustomerDevBase):
    id: str

class CustomerDevByIdSch(CustomerDevFullBase):
    pass

