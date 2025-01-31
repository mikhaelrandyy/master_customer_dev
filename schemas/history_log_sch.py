from models.history_log_model import HistoryLogBase, HistoryLogFullBase


class HistoryLogCreateSch(HistoryLogBase):
    pass

class HistoryLogSch(HistoryLogFullBase):
    pass 

class HistoryLogUpdateSch(HistoryLogBase):
    pass

class HistoryLogByIdSch(HistoryLogFullBase):
    pass

class HistoryLogCreateUpdateSch(HistoryLogBase):
    created_by: str
    updated_by: str

