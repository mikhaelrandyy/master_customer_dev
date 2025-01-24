from fastapi import HTTPException
from fastapi_async_sqlalchemy import db
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from crud.base_crud import CRUDBase
from models import CustomerDev, CustomerDevGroup

from schemas.customer_dev_sch import CustomerDevCreateSch, CustomerDevUpdateSch
from schemas.customer_dev_group_sch import CustomerDevGroupCreateSch
from schemas.history_log_sch import HistoryLogCreateSch
from common.generator import CodeCounterEnum, generate_code, generate_number
from common.enum import CustomerDevTypeEnum, JenisIdentitasTypeEnum
import crud
from ulid import ULID
from typing import List
from random import random
import json


class CRUDCustomerDev(CRUDBase[CustomerDev, CustomerDevCreateSch, CustomerDevUpdateSch]):


    async def get_by_id(self,
                        id:str,
                        db_session: AsyncSession | None = None
                        ) -> CustomerDev:
        
        db_session = db.session

        query = select(CustomerDev)

        query = query.where(CustomerDev.id == id)

        response = await db_session.execute(query)

        return response.scalar_one_or_none()



    async def create_customer_dev(self, *, 
                    sch: list[CustomerDevCreateSch], 
                    created_by : str | None = None,
                    db_session: AsyncSession | None = None
                     ) -> list[CustomerDev]:
        
        db_session = db.session

        customer_devs:list[CustomerDev] = []
        
        for obj_in in sch:
                
                db_obj = CustomerDev.model_validate(obj_in)
                db_obj.created_by = created_by

                db_session.add(db_obj)

                customer_devs.append(db_obj)

        if len(customer_devs) > 1:
                    

                    for obj in customer_devs:
                    
                        obj_parent = await self.create_parent_customer_dev(first_name=obj.first_name, last_name=obj.last_name, created_by=created_by, db_session=db_session, with_commit=False)
                
                        #CREATE CUSTOMER DEV GROUP
                        await self.create_customer_dev_group(customer_parent_id=obj_parent.id, customer_reference_id=obj.id, created_by=created_by, db_session=db_session, with_commit=False)

                    customer_devs.append(obj_parent)

        try:

            for obj in customer_devs:

                if obj.business_id_type in (CustomerDevTypeEnum.PERSON, CustomerDevTypeEnum.ORGANIZATION):

                    await crud.history_log.create_history_log_for_customer(sch=obj, db_session=db_session, with_commit=False)

            await db_session.commit()

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        
        return customer_devs
    
    async def create_parent_customer_dev(self,
                                        *,
                                        first_name: str | None = None,
                                        last_name: str | None = None,
                                        created_by: str | None = None,
                                        db_session: AsyncSession | None = None
                                        ) -> CustomerDev:
        
        db_session = db_session or db.session
        
        combined_names = " & ".join(f"{first_name} {last_name}") + " &"

        parent_db_obj = CustomerDevCreateSch(
                                                type=CustomerDevTypeEnum.PERSON_GROUP,
                                                first_name=combined_names[:40] if len(combined_names) > 40 else combined_names,
                                                last_name=combined_names[40:] if len(combined_names) > 40 else "",
                                                npwp= await generate_number(size=16),
                                                business_id= await generate_number(size=16),
                                                business_id_type=JenisIdentitasTypeEnum.KTP,
                                                nitku= await generate_number(size=22)
                                            )
        
        db_obj = CustomerDev.model_validate(parent_db_obj)
        db_obj.created_by = created_by

        db_session.add(db_obj)

        return db_obj

    async def create_customer_dev_group(self,
                                        *,
                                        customer_parent_id: str | None = None,
                                        customer_reference_id: str | None = None,
                                        created_by: str | None = None,
                                        db_session: AsyncSession | None = None
                                        ) -> CustomerDev:
        

        cust_group = CustomerDevGroupCreateSch(
                                                customer_parent_id=customer_parent_id,
                                                customer_reference_id=customer_reference_id
                                            )
        
        db_obj = CustomerDevGroup.model_validate(cust_group)
        db_obj.created_by = created_by

        db_session.add(db_obj)

        return db_obj
    
    async def update_customer_dev(self, 
                                *, 
                                obj_current: CustomerDev,
                                obj_updated: CustomerDevUpdateSch,
                                updated_by: str | None = None
                            ) -> CustomerDev:
        
        db_session = db.session

        obj_updated = await crud.customer_dev.update(obj_current=obj_current, obj_updated=obj_updated, updated_by=updated_by, db_session=db_session, with_commit=False)
        

        try:

            if obj_updated:

                await crud.history_log.update_history_log_for_customer(obj_current=obj_current, obj_in=obj_updated, db_session=db_session, with_commit=False)

            await db_session.commit()

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=409, detail=str(e))

        return obj_updated


customer_dev = CRUDCustomerDev(CustomerDev)
