from fastapi import HTTPException
from fastapi_async_sqlalchemy import db
from fastapi.encoders import jsonable_encoder
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, exc
from crud.base_crud import CRUDBase
from models import (
    CustomerDev, 
    CustomerDevGroup,
    HistoryLog,
    Attachment)
from schemas.customer_dev_sch import CustomerDevCreateSch, CustomerDevUpdateSch
from schemas.customer_dev_group_sch import CustomerDevGroupCreateSch
from schemas.history_log_sch import HistoryLogCreateSch, HistoryLogCreateUpdateSch
from schemas.attachment_sch import AttachmentSch
from common.generator import generate_number
from common.enum import CustomerDevTypeEnum, JenisIdentitasTypeEnum, NationalityEnum
from sqlalchemy.orm import selectinload, joinedload, with_loader_criteria
import crud



class CRUDCustomerDev(CRUDBase[CustomerDev, CustomerDevCreateSch, CustomerDevUpdateSch]):
    async def get_by_id(self, *, id:str, is_active: bool | None = None) -> CustomerDev:

        query = select(CustomerDev)
        query = query.where(CustomerDev.id == id)
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == is_active) 
                              if is_active is not None else selectinload(CustomerDev.attachments))

        response = await db.session.execute(query)
        
        return response.scalar_one_or_none()

    async def get_by_ids(self, *, ids: list[str], is_active: bool | None = None) -> list[CustomerDev]:
        query = select(CustomerDev).where(CustomerDev.id.in_(ids)) 
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == is_active) 
                              if is_active is not None else selectinload(CustomerDev.attachments))

        response = await db.session.execute(query)
    
        return response.scalars().all()

    async def create(self, *, sch: list[CustomerDevCreateSch], created_by : str | None = None) -> list[CustomerDev]:
        new_customers: list[CustomerDev] = []
        try:
            for obj_in in sch:

                await self.check_validasi(obj_in=obj_in)

                customer_dev = CustomerDev.model_validate(obj_in.model_dump())

                if created_by:
                    customer_dev.created_by = customer_dev.updated_by = created_by

                for attachment in obj_in.attachments:
                    customer_dev.attachments.append(Attachment(**attachment.model_dump(), created_by=created_by, updated_by=created_by, is_active=True))

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
                        before=jsonable_encoder(new_customer),
                        after=jsonable_encoder(new_customer),
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

    async def update_customer_dev(self, *, obj_current: CustomerDev, obj_new: CustomerDevUpdateSch, updated_by: str) -> CustomerDev:
        try:
            await self.check_validasi(obj_in=obj_new)

            obj_before_update = obj_current.model_dump()  

            #UPDATE CUSTOMER
            obj_data = jsonable_encoder(obj_current)

            if isinstance(obj_new, dict):
                update_data = obj_new
            else:
                update_data = obj_new.dict(exclude_unset=True) 

            for field in obj_data:
                if field in update_data:
                    setattr(obj_current, field, update_data[field])
                elif updated_by and updated_by != '' and field == "updated_by":
                    setattr(obj_current, field, updated_by)

            db.session.add(obj_current)

            if obj_new.attachments:
                for attachment in obj_new.attachments:
                    existing_attachment = await crud.attachment.get_by_doc_type(customer_id=obj_new.id, doc_type=attachment.doc_type)

                    if existing_attachment:
                        existing_attachment.is_active = False
                        existing_attachment.updated_by = updated_by
                        db.session.add(existing_attachment)

                    #CREATE NEW ATTACHMENT
                    new_attachment = Attachment.model_validate(attachment.model_dump())
                    new_attachment.is_active = True
                    new_attachment.updated_by = updated_by
                    new_attachment.created_by = updated_by
                    db.session.add(new_attachment)

            history_log_entry = HistoryLogCreateUpdateSch(
                                                reference_id=obj_new.id, 
                                                before=obj_before_update,  
                                                after=obj_current.model_dump(), 
                                                source_process=obj_new.lastest_source_from,
                                                source_table="customer_dev",
                                                updated_by=updated_by,
                                                created_by=updated_by
                                            )
            hislog_db = HistoryLog.model_validate(history_log_entry.model_dump())
            db.session.add(hislog_db)

            await db.session.commit()
            await db.session.refresh(obj_current)

        except exc.IntegrityError as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e._message))
        except Exception as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))

        return obj_current
    
    async def check_validasi(self, *, obj_in: CustomerDevCreateSch | CustomerDevUpdateSch):
        if obj_in.type == CustomerDevTypeEnum.PERSON and obj_in.business_id_type != {JenisIdentitasTypeEnum.KTP, JenisIdentitasTypeEnum.KIA, JenisIdentitasTypeEnum.PASPOR}:
                raise HTTPException(status_code=400, detail=f"Invalid business_type {obj_in.business_id_type} for PERSON. Allowed: KTP, KIA, PASPOR.")
            
        if obj_in.type == CustomerDevTypeEnum.ORGANIZATION:
            if obj_in.business_id_type != {JenisIdentitasTypeEnum.NIB}:
                raise HTTPException(status_code=400, detail=f"Invalid business_type {obj_in.business_id_type} for ORGANIZATION. Allowed: NIB.")
            if not obj_in.business_establishment_number:
                raise HTTPException(status_code=400, detail="business_establishment_number is required for ORGANIZATION.")

        if obj_in.business_id_type == JenisIdentitasTypeEnum.KTP:
            if len(obj_in.business_id) != 16:
                raise HTTPException(status_code=400, detail=f"Invalid KTP length. Must be 16 digits.")
            
        if obj_in.business_id_type == JenisIdentitasTypeEnum.KIA:
            if len(obj_in.business_id) != 16:
                raise HTTPException(status_code=400, detail=f"Invalid KIA length. Must be 16 digits.")

        if obj_in.business_id_type == JenisIdentitasTypeEnum.PASPOR:
            if obj_in.marital_status != "-":
                raise HTTPException(status_code=400, detail=f"Invalid marital_status. Must be -.")
            if len(obj_in.business_id) != 8:
                raise HTTPException(status_code=400, detail=f"Invalid PASPOR length. Must be 8 digits.")
            
        if obj_in.business_id_type == JenisIdentitasTypeEnum.NIB:
            if len(obj_in.business_id) != 13:
                raise HTTPException(status_code=400, detail=f"Invalid NIB length. Must be 13 digits.")

        if obj_in.type in (CustomerDevTypeEnum.PERSON_GROUP, CustomerDevTypeEnum.ORGANIZATION):
            if obj_in.gender != None:
                raise HTTPException(status_code=400, detail=f"Invalid gender. Must be None.")
        
        if obj_in.type in (CustomerDevTypeEnum.PERSON, CustomerDevTypeEnum.ORGANIZATION): 
            if obj_in.nitku:
                if len(obj_in.nitku) != 22:
                    raise HTTPException(status_code=400, detail=f"Invalid NITKU length. Must be 22 digits.")


customer_dev = CRUDCustomerDev(CustomerDev)
