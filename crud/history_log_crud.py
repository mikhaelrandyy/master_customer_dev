from crud.base_crud import CRUDBase
from models import HistoryLog

from schemas.history_log_sch import HistoryLogCreateSch
from schemas.customer_dev_group_sch import HistoryLogCreateSch, HistoryLogUpdateSch
from schemas.customer_dev_sch import CustomerDevSch
import crud




class CRUDHistoryLog(CRUDBase[HistoryLog, HistoryLogCreateSch, HistoryLogUpdateSch]):
    
    async def create_history_log_for_customer(self, 
                    *, 
                    obj_in: CustomerDevSch,
                    with_commit: bool | None = True,
                    db_session
                  ) -> HistoryLog | None:


            history_log_entry = HistoryLogCreateSch(
                                                reference_id=obj_in.id, 
                                                before=None,  
                                                after=obj_in, 
                                                source_process="CREATE",
                                                source_table="customer_dev"
                                            )

            new_obj = await crud.history_log.create(obj_in=history_log_entry, db_session=db_session, with_commit=False)

            return new_obj
        
        
    
     
history_log = CRUDHistoryLog(HistoryLog)
