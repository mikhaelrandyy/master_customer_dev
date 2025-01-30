from fastapi import HTTPException
from fastapi_async_sqlalchemy import db
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from crud.base_crud import CRUDBase
from models import (
    CustomerDev, 
    CustomerDevGroup,
    HistoryLog)
from schemas.customer_dev_sch import CustomerDevCreateSch, CustomerDevUpdateSch
from schemas.customer_dev_group_sch import CustomerDevGroupCreateSch
from schemas.history_log_sch import HistoryLogCreateSch
from common.generator import generate_number
from common.enum import CustomerDevTypeEnum, JenisIdentitasTypeEnum
import crud



class CRUDCustomerDev(CRUDBase[CustomerDev, CustomerDevCreateSch, CustomerDevUpdateSch]):
    async def create(self, *, sch: list[CustomerDevCreateSch], created_by : str | None = None) -> list[CustomerDev]:
        new_customers: list[CustomerDev] = []
        try:
            for obj_in in sch:
                customer_dev = CustomerDev.model_validate(obj_in)

                if created_by:
                    customer_dev.created_by = customer_dev.updated_by = created_by

                db.session.add(customer_dev)
                await db.session.flush()
                new_customers.append(customer_dev)


            # IF CUSTOMER DEV IS MORE THAN 1, THEN CREATE CUSTOMER DEV PERSON GROUP
            if len(sch) > 1:
                combined_names = " & ".join([f"{cust.first_name or ''} {cust.last_name or ''}".strip() for cust in new_customers])
                customer_dev_person_group = await self.create_customer_person_group(combined_names=combined_names, created_by=created_by)

                # THEN MAPPING CUSTOMER DEV PERSON WITH CUSTOMER DEV PERSON GROUP
                await self.create_customer_group(person_customer_ids=[cust.id for cust in new_customers], person_group_customer_id=customer_dev_person_group.id, created_by=created_by)
                new_customers.append(customer_dev_person_group)

            # CREATE FIRST HISTORY LOG
            for new_customer in new_customers:

                if new_customer.business_id_type != CustomerDevTypeEnum.PERSON_GROUP:

                    history_log_entry = HistoryLogCreateSch(
                        reference_id=new_customer.id,
                        before=None,
                        after=new_customer.model_dump(),
                        source_process=new_customer.lastest_source_from,
                        source_table="customer_dev")

                    history_log = HistoryLog.model_validate(history_log_entry.model_dump())
                    db.session.add(history_log)
            
            await db.session.commit()

        except Exception as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        
        return new_customers
    
    async def create_customer_person_group(self, *, combined_names:str, created_by:str) -> CustomerDev:
        customer_dev_person_group: CustomerDevCreateSch = None
        customer_dev_person_group.type = CustomerDevTypeEnum.PERSON_GROUP
        customer_dev_person_group.first_name = combined_names[:40] if len(combined_names) > 40 else combined_names
        customer_dev_person_group.last_name = combined_names[40:] if len(combined_names) > 40 else ""
        customer_dev_person_group.npwp = generate_number(digit=16)
        customer_dev_person_group.business_id = generate_number(digit=16)
        customer_dev_person_group.business_id_type = JenisIdentitasTypeEnum.KTP
        customer_dev_person_group.nitku = generate_number(digit=22)
                                            
        db_obj = CustomerDev.model_validate(customer_dev_person_group.model_dump())
        if created_by:
            db_obj.created_by = db_obj.updated_by = created_by
        db.session.add(db_obj)
        await db.session.flush()
        return db_obj
    
    async def create_customer_group(self, *, person_customer_ids:list[str], person_group_customer_id:str, created_by:str):
        for person_customer_id in person_customer_ids:
            customer_dev_group: CustomerDevGroupCreateSch = None
            customer_dev_group.customer_parent_id = person_group_customer_id
            customer_dev_group.customer_reference_id = person_customer_id

            db_obj = CustomerDevGroup.model_validate(customer_dev_group.model_dump())
            if created_by:
                db_obj.created_by = db_obj.updated_by = created_by

            db.session.add(db_obj)

customer_dev = CRUDCustomerDev(CustomerDev)
