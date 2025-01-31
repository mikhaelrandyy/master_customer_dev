from fastapi import APIRouter, status, Depends, UploadFile, HTTPException, Response

from schemas.customer_dev_sch import (CustomerDevSch, CustomerDevCreateSch, CustomerDevByIdSch, CustomerDevUpdateSch, CustomerDevForAttachmentSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, GetResponsePaginatedSch, PutResponseBaseSch, create_response)

from models import CustomerDev
from models.customer_dev_model import Worker
import crud

router = APIRouter()

@router.post("", response_model=PostResponseBaseSch[list[CustomerDevSch]], status_code=status.HTTP_201_CREATED)
async def create(sch: list[CustomerDevCreateSch]):
    
    """Create a new object"""

    obj = await crud.customer_dev.create(sch=sch)

    return create_response(data=obj)

@router.put("", response_model=PostResponseBaseSch[CustomerDevSch], status_code=status.HTTP_201_CREATED)
async def update(sch: CustomerDevUpdateSch):
    
    """Create a new object"""

    obj_current = await crud.customer_dev.get(id=sch.id)

    if not obj_current:
        raise HTTPException(status_code=404, detail=f"Customer tidak ditemukan")

    obj_updated = await crud.customer_dev.update_customer_dev(obj_current=obj_current, obj_new=sch)

    response_obj = await crud.customer_dev.get_by_id(id=obj_updated.id)

    return create_response(data=response_obj)