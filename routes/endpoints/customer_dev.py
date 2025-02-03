from fastapi import APIRouter, status, Depends, HTTPException
from fastapi_pagination import Params
from sqlmodel import select

from schemas.customer_dev_sch import (CustomerDevSch, CustomerDevCreateSch, CustomerDevUpdateSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, GetResponsePaginatedSch, PutResponseBaseSch, create_response)
from models.customer_dev_model import CustomerDev
import crud
from utils.exceptions.common_exception import IdNotFoundException

router = APIRouter()

@router.get("/{id}", response_model=GetResponseBaseSch[CustomerDevSch])
async def get_by_id(id: str, is_active: bool | None = None):

    obj = await  crud.customer_dev.get_by_id(id=id, is_active=is_active)

    if obj is None:
        raise IdNotFoundException(CustomerDev, id)

    return create_response(data=obj)

@router.post("", response_model=PostResponseBaseSch[list[CustomerDevSch]], status_code=status.HTTP_201_CREATED)
async def create(sch: list[CustomerDevCreateSch]):
    
    """Create a new object"""

    obj = await crud.customer_dev.create(sch=sch)
    response_obj = await crud.customer_dev.get_by_ids(ids=[cust.id for cust in obj], is_active=True)
    return create_response(data=response_obj)

@router.put("", response_model=PostResponseBaseSch[CustomerDevSch], status_code=status.HTTP_201_CREATED)
async def update(sch: CustomerDevUpdateSch):
    
    """Create a new object"""

    obj_current = await crud.customer_dev.get(id=sch.id)
    if not obj_current:
        raise HTTPException(status_code=404, detail=f"Customer tidak ditemukan")

    obj_updated = await crud.customer_dev.update_customer_dev(obj_current=obj_current, obj_new=sch, updated_by=None)
    response_obj = await crud.customer_dev.get_by_id(id=obj_updated.id, is_active=True)

    return create_response(data=response_obj)