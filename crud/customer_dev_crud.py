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
from schemas.customer_dev_sch import CustomerDevCreateSch, CustomerDevUpdateSch, CustomerDevByIdSch, CustomerDevSch, ChangeDataSch
from schemas.attachment_sch import AttachmentUpdateSch, AttachmentCreateSch
from schemas.customer_dev_group_sch import CustomerDevGroupCreateSch
from schemas.history_log_sch import HistoryLogCreateSch
from common.generator import generate_number
from common.enum import CustomerDevEnum, JenisIdentitasEnum
from sqlalchemy.orm import selectinload, with_loader_criteria
import crud
from enum import Enum
from datetime import datetime, date
import json

class CRUDCustomerDev(CRUDBase[CustomerDev, CustomerDevCreateSch, CustomerDevUpdateSch]):

    async def create_bulk(self, *, sch: list[CustomerDevCreateSch], created_by : str | None = None):
        objs = []
        try:
            for obj_new in sch:
                # self.check_validasi(obj_in=obj_in.model_dump())
                customerdev = await self.get_by_business_id(business_id=obj_new.business_id)
                if customerdev:
                    customerdev_updated = CustomerDevUpdateSch(**customerdev.model_dump())
                    customerdev = await self.update(obj_current=customerdev, obj_new=customerdev_updated, updated_by=created_by, with_commit=False)
                else:
                    customerdev_created = CustomerDevCreateSch(**obj_new.model_dump())
                    customerdev = await self.create(obj_in=customerdev_created, created_by=created_by, with_commit=False)
                
                for obj_new_attach in obj_new.attachments:
                    current_attachment = await crud.attachment.get_actived_attachment(
                        customer_id=customerdev.id, 
                        doc_type=obj_new_attach.doc_type
                    )

                    if current_attachment:
                        attachment_updated = AttachmentUpdateSch(**current_attachment.model_dump())
                        attachment_updated.is_active = False
                        await crud.attachment.update(obj_current=current_attachment, obj_new=attachment_updated, updated_by=created_by, with_commit=False)

                    attachment_created = AttachmentCreateSch(**obj_new_attach.model_dump())
                    attachment_created.customer_id = customerdev.id
                    attachment_created.is_active = True
                    await crud.attachment.create(obj_in=attachment_created, created_by=created_by, with_commit=False)
                
                customerdev_return = customerdev.model_dump()
                customerdev_return["reference_id"] = obj_new.reference_id
                objs.append(customerdev_return)

            # IF CUSTOMER DEV IS MORE THAN 1, THEN CREATE CUSTOMER DEV PERSON GROUP
            if len(sch) > 1:
                # CREATE CUSTOMER DEV PERSON GROUP
                customerdev_person_group = await self.create_customer_person_group(objs=objs, created_by=created_by)

                # MAPPING CUSTOMER DEV PERSON WITH CUSTOMER DEV PERSON GROUP
                await self.create_customer_group(person_customer_ids=[cust["id"] for cust in objs], person_group_customer_id=customerdev_person_group.id)
                customerdev_person_group_return = customerdev_person_group.model_dump()
                customerdev_person_group_return["reference_id"] = None
                objs.append(customerdev_person_group_return)

            await db.session.commit()

        except Exception as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        
        return objs
    
    async def create_customer_person_group(self, *, objs, created_by:str) -> CustomerDev:
        combined_names = " & ".join([f"{cust["first_name"] or ''} {cust["last_name"] or ''}".strip() for cust in objs])
        required_fields = ["type", "first_name", "last_name",    
            "business_id_type", "business_id", "npwp",
            "nitku", "code", "gender",
            "religion", "marital_status", "mailing_address_type",
            "business_id_creation_date", "business_id_valid_until", "date_of_birth",
            "email", "attachments"
        ]

        customerdev_person_group_created = CustomerDevCreateSch(
            type=CustomerDevEnum.PERSON_GROUP,
            first_name=combined_names[:80] if len(combined_names) > 80 else combined_names,
            last_name=combined_names[80:] if len(combined_names) > 80 else "",
            business_id_type=JenisIdentitasEnum.KTP,
            business_id=str(generate_number(digit=16)),
            npwp=str(generate_number(digit=16)),
            nitku=str(generate_number(digit=22))
        )
        
        for field in customerdev_person_group_created.__fields__:
            if field not in required_fields:
                setattr(customerdev_person_group_created, field, "-")


        customerdev_person_group = await crud.customer_dev.create(obj_in=customerdev_person_group_created, created_by=created_by, with_commit=False)
        return customerdev_person_group
    
    async def create_customer_group(self, *, person_customer_ids:list[str], person_group_customer_id:str):
        for person_customer_id in person_customer_ids:
            customer_dev_group = CustomerDevGroupCreateSch(customer_parent_id = person_group_customer_id, customer_reference_id = person_customer_id)

            db_obj = CustomerDevGroup(**customer_dev_group.model_dump())

            db.session.add(db_obj)
    
    async def update_change_data(self, *, obj_current: CustomerDev, obj_new: ChangeDataSch, updated_by: str) -> CustomerDev:
        try:
            if obj_new.lastest_source_from is None:
                raise HTTPException(status_code=400, detail="source_process is required.")
            
            if obj_new.vs_reference is None:
                raise HTTPException(status_code=400, detail="vs_reference is required.")

            if obj_new.before is None or obj_new.after is None:
                raise HTTPException(status_code=400, detail="Data 'before' dan 'after' wajib dikirim untuk melakukan perubahan.")
            
            # self.check_validasi(obj_in=obj_after)

            customerdev = await self.update(obj_current=obj_current, obj_new=obj_new.after, updated_by=updated_by, with_commit=False)

            if 'attachments' in obj_new.after:
                for obj_new_attach in obj_new.after.get('attachments'):
                    current_attachment = await crud.attachment.get_actived_attachment(
                        customer_id=obj_current.id, 
                        doc_type=obj_new_attach.get('doc_type')
                    )

                    if current_attachment:
                        attachment_updated = AttachmentUpdateSch(**current_attachment.model_dump())
                        attachment_updated.is_active = False
                        await crud.attachment.update(obj_current=current_attachment, obj_new=attachment_updated, updated_by=updated_by, with_commit=False)

                    attachment_created = AttachmentCreateSch(**obj_new_attach.model_dump())
                    attachment_created.customer_id = customerdev.id
                    attachment_created.is_active = True
                    await crud.attachment.create(obj_in=attachment_created, created_by=updated_by, with_commit=False)
                

            # Log perubahan
            history_log_created = HistoryLogCreateSch(
                reference_id=obj_current.id,
                before=jsonable_encoder(obj_new.before),
                after=jsonable_encoder(obj_new.after),
                source_process=obj_new.lastest_source_from,
                vs_reference=obj_new.vs_reference,
                source_table="customer_dev",
                created_by=updated_by,
                updated_by=updated_by
            )
            await crud.history_log.create(obj_in=history_log_created, created_by=updated_by, with_commit=False)

            await db.session.commit()
            await db.session.refresh(obj_current)

        except exc.IntegrityError as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e._message))
        except Exception as e:
            await db.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))

        return obj_current
    
    async def get_by_id(self, *, id:str) -> CustomerDev | None:

        query = select(CustomerDev)
        query = query.where(CustomerDev.id == id)
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == True))

        response = await db.session.execute(query)
        return response.scalar_one_or_none()
    
    async def get_by_ids(self, *, ids: list[str]) -> list[CustomerDevByIdSch]:
        
        query = select(CustomerDev).where(CustomerDev.id.in_(ids)) 
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == True))

        response = await db.session.execute(query)
        return response.scalars().all()

    async def get_by_business_id(self, *, business_id:str) -> CustomerDev | None:
        query = select(CustomerDev)
        query = query.where(
            or_(CustomerDev.business_id == business_id, 
                CustomerDev.npwp == business_id,
                CustomerDev.nitku == business_id
            )
        )
        query = query.options(selectinload(CustomerDev.attachments), with_loader_criteria(Attachment, Attachment.is_active == True))

        response = await db.session.execute(query)
        return response.scalar_one_or_none()
    
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

