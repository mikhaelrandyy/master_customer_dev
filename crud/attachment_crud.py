from fastapi_async_sqlalchemy import db
from sqlmodel import and_, select
from crud.base_crud import CRUDBase
from models import Attachment
from schemas.attachment_sch import AttachmentCreateSch, AttachmentUpdateSch




class CRUDAttachment(CRUDBase[Attachment, AttachmentCreateSch, AttachmentUpdateSch]):
    
    async def get_by_customer_id(self, *, customer_id: str | None = None) -> Attachment | None:
        
        query = select(Attachment)
        query = query.where(Attachment.customer_id == customer_id)
        response = await db.session.execute(query)

        return response.scalar_one_or_none()
    
    async def get_actived_attachment(self, *, customer_id: str | None = None, doc_type: str | None = None) -> Attachment:
        query = select(Attachment)
        query = query.where(and_(
                            Attachment.customer_id == customer_id,
                            Attachment.doc_type == doc_type,
                            Attachment.is_active == True
                        )
                    )
        response = await db.session.execute(query)

        return response.scalar_one_or_none()
     
attachment = CRUDAttachment(Attachment)
