from sqlmodel import select
from fastapi_async_sqlalchemy import db
from crud.base_crud import CRUDBase
from schemas.history_log_sch import HistoryLogCreateSch, HistoryLogUpdateSch
from schemas.customer_dev_sch import CustomerDevSch, CustomerDevUpdateSch, CustomerDevCreateSch

from models import HistoryLog, CustomerDev

import crud
import json




class CRUDHistoryLog(CRUDBase[HistoryLog, HistoryLogCreateSch, HistoryLogUpdateSch]):

    async def get_by_reference_ids(self, *, reference_ids: list[str]) -> list[HistoryLog]:
        query = select(HistoryLog).where(HistoryLog.reference_id.in_(reference_ids)) 
        response = await db.session.execute(query)
        return response.scalars().all()

    async def get_by_reference_id(self, *, reference_id: str) -> HistoryLog:
        query = select(HistoryLog).where(HistoryLog.reference_id == reference_id) 
        response = await db.session.execute(query)
        return response.scalar_one_or_none()
    
    async def create_history_log_for_customer(self, *, obj_in: CustomerDev, created_by: str | None = None, db_session) -> HistoryLog:
            history_log_entry = HistoryLogCreateSch(
                                                reference_id=obj_in.id, 
                                                before=None,  
                                                after=obj_in, 
                                                source_process="CREATE",
                                                source_table="customer_dev"
                                            )
            db_obj = HistoryLog.model_validate(history_log_entry)
            db_obj.created_by = created_by
            db_session.add(db_obj)

            return db_obj
    
    async def update_history(self, *, obj_current: CustomerDev, obj_in: CustomerDevUpdateSch, updated_by: str | None = None, db_session) -> HistoryLog | None:
            history_log_entry = HistoryLogUpdateSch(
                                                reference_id=obj_in.id, 
                                                before=obj_current.model_dump(),  
                                                after=obj_in.model_dump(), 
                                                source_process=obj_current.lastest_source_from,
                                                source_table="customer_dev",
                                                updated_by=updated_by
                                            )
            db_obj = HistoryLog.model_validate(history_log_entry)
            db_session.add(db_obj)

            return db_obj
        
        
    
     
history_log = CRUDHistoryLog(HistoryLog)
