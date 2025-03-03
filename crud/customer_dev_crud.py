from fastapi import HTTPException
from fastapi_async_sqlalchemy import db
from fastapi.encoders import jsonable_encoder
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_
from sqlalchemy import select, exc
from crud.base_crud import CRUDBase
from models import (
    CustomerDev, 
    CustomerDevGroup,
    HistoryLog,
    Attachment)
from schemas.customer_dev_sch import CustomerDevCreateSch, CustomerDevUpdateSch, CustomerDevByIdSch, CustomerDevSch
from schemas.customer_dev_group_sch import CustomerDevGroupCreateSch
from schemas.history_log_sch import HistoryLogCreateUpdateSch
from services.pubsub_service import PubSubService
from common.generator import generate_number
from common.enum import CustomerDevEnum, JenisIdentitasEnum
from sqlalchemy.orm import selectinload, with_loader_criteria
import crud
from enum import Enum
from datetime import datetime, date
import json

class CRUDCustomerDev(CRUDBase[CustomerDev, CustomerDevCreateSch, CustomerDevUpdateSch]):
    async def get_by_id(self, *, id:str, is_active: bool | None = None) -> CustomerDev:

        query = select(CustomerDev)
        query = query.where(CustomerDev.id == id)
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == is_active) 
                              if is_active is not None else selectinload(CustomerDev.attachments))

        response = await db.session.execute(query)
        return response.scalar_one_or_none()
    
    async def get_by_business_id(self, *, business_id:str) -> CustomerDev:

        query = select(CustomerDev)
        query = query.where(or_(CustomerDev.business_id == business_id, 
                                CustomerDev.npwp == business_id,
                                CustomerDev.nitku == business_id))
        query = query.options(selectinload(CustomerDev.attachments))

        response = await db.session.execute(query)
        
        return response.scalar_one_or_none()

    async def get_by_ids(self, *, ids: list[str], is_active: bool | None = None) -> list[CustomerDevByIdSch]:
        query = select(CustomerDev).where(CustomerDev.id.in_(ids)) 
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == is_active) 
                              if is_active is not None else selectinload(CustomerDev.attachments))

        response = await db.session.execute(query)
    
        return response.scalars().all()

    async def create(self, *, sch: list[CustomerDevCreateSch], created_by : str | None = None) -> list[CustomerDevSch]:
        new_customers: list[CustomerDevByIdSch] = []
        new_customer: list[CustomerDevSch] = []
        try:
            for obj_in in sch:
                existing_customer = await self.get_by_business_id(business_id=obj_in.business_id)
                if existing_customer:
                    new_customer.append(existing_customer)
                    continue
                
                # self.check_validasi(obj_in=obj_in.model_dump())

                customer_dev = CustomerDev.model_validate(obj_in.model_dump())

                if created_by:
                    customer_dev.created_by = customer_dev.updated_by = created_by

                for attachment in obj_in.attachments:
                    attachment_obj = Attachment(**attachment.model_dump(), created_by=created_by, updated_by=created_by, is_active=True)
                    customer_dev.attachments.append(attachment_obj)

                db.session.add(customer_dev)
                await db.session.flush()
                await db.session.refresh(customer_dev, ["attachments"])

                customer_obj = CustomerDevByIdSch(**customer_dev.model_dump(), reference_id=obj_in.reference_id, attachments=[attachment.model_dump() for attachment in customer_dev.attachments])
                new_customers.append(customer_obj)
                new_customer.append(customer_obj)

            # IF CUSTOMER DEV IS MORE THAN 1, THEN CREATE CUSTOMER DEV PERSON GROUP
            if len(sch) > 1:
                combined_names = " & ".join([f"{cust.first_name or ''} {cust.last_name or ''}".strip() for cust in new_customers])
                customer_dev_person_group = await self.create_customer_person_group(combined_names=combined_names, created_by=created_by)

                # THEN MAPPING CUSTOMER DEV PERSON WITH CUSTOMER DEV PERSON GROUP
                await self.create_customer_group(person_customer_ids=[cust.id for cust in new_customers], person_group_customer_id=customer_dev_person_group.id, created_by=created_by)
                new_customers.append(customer_dev_person_group)
                new_customer.append(customer_dev_person_group)

            await db.session.commit()

            for obj_pubsub in new_customers:
                PubSubService().publish_to_pubsub(topic_name="master-customerdev", message=obj_pubsub, action="create")
                mapping_cust_group = await crud.customer_dev_group.get_multi_by_reference_id(id=obj_in.id)

        except Exception as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        
        return new_customer
    
    async def create_customer_person_group(self, *, combined_names:str, created_by:str) -> CustomerDev:
        required_fields = {
            "type": CustomerDevEnum.PERSON_GROUP,
            "first_name": combined_names[:40] if len(combined_names) > 40 else combined_names,
            "last_name": combined_names[40:] if len(combined_names) > 40 else "",    
            "business_id_type": JenisIdentitasEnum.KTP,
            "business_id": str(generate_number(digit=16)),
            "npwp": str(generate_number(digit=16)),
            "nitku": str(generate_number(digit=22)),
            "code": None,
            "gender": None,
            "religion": None,
            "marital_status": None,
            "mailing_address_type": None,
            "business_id_creation_date": None,
            "business_id_valid_until": None,
            "date_of_birth": None,
            "email": None,
            "attachments": []
        }
        customer_dev_person_group = CustomerDevCreateSch.model_construct(**required_fields)
        
        for field in customer_dev_person_group.__fields__:
            if field not in required_fields:
                setattr(customer_dev_person_group, field, "-")


        db_obj = CustomerDev(**customer_dev_person_group.model_dump())

        if created_by:
            db_obj.created_by = db_obj.updated_by = created_by
        db.session.add(db_obj)
        await db.session.flush()
        return db_obj
    
    async def create_customer_group(self, *, person_customer_ids:list[str], person_group_customer_id:str):
        for person_customer_id in person_customer_ids:
            customer_dev_group = CustomerDevGroupCreateSch(customer_parent_id = person_group_customer_id, customer_reference_id = person_customer_id)

            db_obj = CustomerDevGroup(customer_dev_group.model_dump())

            db.session.add(db_obj)
    
    async def update_customer_dev(self, *, obj_current: CustomerDev, obj_new: dict, updated_by: str) -> CustomerDev:
        try:
            obj_after = obj_new.get('after')
            obj_before = obj_new.get('before')
            source_process = obj_new.get('lastest_source_from')
            vs_reference = obj_new.get('vs_reference')

            if source_process is None:
                raise HTTPException(status_code=400, detail="source_process is required.")
            
            if vs_reference is None:
                raise HTTPException(status_code=400, detail="vs_reference is required.")

            if obj_before is None or obj_after is None:
                raise HTTPException(status_code=400, detail="Data 'before' dan 'after' wajib dikirim untuk melakukan perubahan.")
            
            # self.check_validasi(obj_in=obj_after)

            date_fields = ['business_id_creation_date', 'business_id_valid_until', 'date_of_birth']

            for field in date_fields:
                if field in obj_after:
                    obj_after[field] = datetime.strptime(obj_after[field], '%Y-%m-%d').date()

            for field in obj_after.keys():
                if field != 'attachments' and hasattr(obj_current, field):
                    setattr(obj_current, field, obj_after[field])

            obj_current.updated_by = updated_by
            obj_current.updated_at = datetime.utcnow()

            db.session.add(obj_current)

            if 'attachments' in obj_after:
                for attachment in obj_after.get('attachments'):
                    existing_attachment = await crud.attachment.get_by_doc_type(customer_id=obj_current.id, doc_type=attachment.get('doc_type'))

                    if existing_attachment:
                        existing_attachment.is_active = False
                        existing_attachment.updated_by = updated_by
                        db.session.add(existing_attachment)

                    # Create new attachment
                    new_attachment = Attachment(**attachment)
                    new_attachment.customer_id = obj_current.id
                    new_attachment.is_active = True
                    new_attachment.updated_by = updated_by
                    new_attachment.created_by = updated_by
                    db.session.add(new_attachment)

            # Log perubahan
            history_log_entry = HistoryLogCreateUpdateSch(
                reference_id=obj_current.id,
                before=jsonable_encoder(obj_new.get('before')),
                after=jsonable_encoder(obj_new.get('after')),
                source_process=source_process,
                vs_reference=vs_reference,
                source_table="customer_dev",
                created_by=updated_by,
                updated_by=updated_by
            )
            hislog_db = HistoryLog.model_validate(history_log_entry.model_dump())
            db.session.add(hislog_db)

            await db.session.commit()
            await db.session.refresh(obj_current)
            # PubSubService().publish_to_pubsub(topic_name="master-customerdev", message=obj_current, action="update")

        except exc.IntegrityError as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e._message))
        except Exception as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))

        return obj_current
    
    # def check_validasi(self, *, obj_in: dict):

    #     type_customer = obj_in.get('type', None)
    #     business_id_type = obj_in.get('business_id_type', None)
    #     business_id = obj_in.get('business_id', None)
    #     marital_status = obj_in.get('marital_status', None)
    #     nitku = obj_in.get('nitku', None)
    #     business_establishment_number = obj_in.get('business_establishment_number', None)
    #     gender = obj_in.get('gender', None)

    #     if "business_id" in obj_in and business_id is None:
    #         raise HTTPException(status_code=400, detail="Identity Number is required.")

    #     if business_id:
    #         if not business_id_type:
    #             raise HTTPException(status_code=400, detail="business_id_type is required when changing business_id.")

    #         if business_id_type == JenisIdentitasEnum.KTP:
    #             if len(business_id) != 16:
    #                 raise HTTPException(status_code=400, detail=f"Invalid KTP length. Must be 16 digits.")

    #         if business_id_type == JenisIdentitasEnum.KIA:
    #             if len(business_id) != 16:
    #                 raise HTTPException(status_code=400, detail=f"Invalid KIA length. Must be 16 digits.")

    #         if business_id_type == JenisIdentitasEnum.PASPOR:
    #             if marital_status:
    #                 if marital_status != "-":
    #                     raise HTTPException(status_code=400, detail=f"Marital_status is invalid. Must - and cannot be null")
                    
    #             if "marital_status" in obj_in and marital_status is None:
    #                 raise HTTPException(status_code=400, detail="Marital Status is required.")
                    
    #             if len(business_id) != 8:
    #                 raise HTTPException(status_code=400, detail=f"Invalid PASPOR length. Must be 8 digits.")

    #         if business_id_type == JenisIdentitasEnum.NIB:
    #             if len(business_id) != 13:
    #                 raise HTTPException(status_code=400, detail=f"Invalid NIB length. Must be 13 digits.")
        
    #     if type_customer == CustomerDevEnum.PERSON:
    #         if business_id_type not in {JenisIdentitasEnum.KTP, JenisIdentitasEnum.KIA, JenisIdentitasEnum.PASPOR}:
    #             raise HTTPException(status_code=400, detail=f"Invalid business_type {business_id_type} for PERSON. Allowed: KTP, KIA, PASPOR.")

    #     if type_customer == CustomerDevEnum.ORGANIZATION:
    #         if business_id_type not in {JenisIdentitasEnum.NIB}:
    #             raise HTTPException(status_code=400, detail=f"Invalid business_type {business_id_type} for ORGANIZATION. Allowed: NIB.")
    #         if not business_establishment_number:
    #             raise HTTPException(status_code=400, detail="business_establishment_number is required for ORGANIZATION.")

    #     if type_customer in (CustomerDevEnum.PERSON_GROUP, CustomerDevEnum.ORGANIZATION):
    #         if gender is not None:
    #             raise HTTPException(status_code=400, detail=f"Invalid gender. Must be None.")

    #     if type_customer in (CustomerDevEnum.PERSON, CustomerDevEnum.ORGANIZATION):
    #         if nitku is None:
    #             raise HTTPException(status_code=400, detail=f"Invalid NITKU length. Must be 22 digits.")

customer_dev = CRUDCustomerDev(CustomerDev)

