from fastapi import HTTPException
from fastapi_async_sqlalchemy import db
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from crud.base_crud import CRUDBase
from models import CustomerDevGroup

from schemas.customer_dev_group_sch import CustomerDevGroupCreateSch, CustomerDevGroupUpdateSch
from sqlalchemy.orm import selectinload




class CRUDCustomerDevGroup(CRUDBase[CustomerDevGroup, CustomerDevGroupCreateSch, CustomerDevGroupUpdateSch]):
    
    async def get_by_id(self, *, id: str | None = None, db_session: AsyncSession | None = None) -> CustomerDevGroup | None:
        db_session = db_session or db.session
        
        query = select(CustomerDevGroup)
        query = query.where(CustomerDevGroup.id == id)
        response = await db_session.execute(query)

        return response.scalar_one_or_none()
    
    async def get_multi_by_reference_id(self, *, id: str | None = None, db_session: AsyncSession | None = None):
        db_session = db_session or db.session
        
        query = select(CustomerDevGroup).where(CustomerDevGroup.customer_reference_id == id)
        response = await db_session.execute(query)

        return response.scalars().all()
    
customer_dev_group = CRUDCustomerDevGroup(CustomerDevGroup)
