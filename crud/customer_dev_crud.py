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
from common.generator import CodeCounterEnum, generate_code, generate_number_16_digit, generate_number_22_digit
from common.enum import CustomerDevTypeEnum, JenisIdentitasTypeEnum
import crud
from ulid import ULID
from typing import List
from random import random
import json


class CRUDCustomerDev(CRUDBase[CustomerDev, CustomerDevCreateSch, CustomerDevUpdateSch]):


    async def create_customer_dev(self, *, 
                     sch: list[CustomerDevCreateSch], 
                     created_by : str | None = None
                     ) -> list[CustomerDev]:
        
        db_session = db.session

        customer_devs:list[CustomerDev] = []
        
        for obj_in in sch:
                
                db_obj = CustomerDevCreateSch.model_validate(obj_in)

                new_obj_cust_dev = await crud.customer_dev.create(obj_in=db_obj, created_by=created_by, db_session=db_session, with_commit=False)

                customer_devs.append(new_obj_cust_dev)

        if len(customer_devs) > 1:

            combined_names = " & ".join([f"{cust.first_name} {cust.last_name}" for cust in customer_devs]) + " &"

            parent_db_obj = CustomerDevCreateSch(
                                                first_name=combined_names[:40] if len(combined_names) > 40 else combined_names,
                                                last_name=combined_names[40:] if len(combined_names) > 40 else "",
                                                npwp=generate_number_16_digit(),
                                                business_id=generate_number_16_digit(),
                                                business_id_type=JenisIdentitasTypeEnum.KTP,
                                                nitku=generate_number_22_digit()
                                            )

            parent_cust_dev = await crud.customer_dev.create(obj_in=parent_db_obj, created_by=created_by, db_session=db_session, with_commit=False)
                
            customer_devs.append(parent_cust_dev)

            for cust_dev in customer_devs:

                cust_group = CustomerDevGroupCreateSch(
                                                        customer_parent_id=parent_cust_dev.id,
                                                        customer_reference_id=cust_dev.id
                                                    )

                await crud.customer_dev_group.create(obj_in=cust_group, db_session=db_session, with_commit=False)

        try:

            for obj in customer_devs:

                if obj.business_id_type in (CustomerDevTypeEnum.PERSON, CustomerDevTypeEnum.ORGANIZATION):

                    await crud.history_log.create_history_log_for_customer(sch=obj, db_session=db_session, with_commit=False)

            await db_session.commit()

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        
        return customer_devs


customer_dev = CRUDCustomerDev(CustomerDev)
