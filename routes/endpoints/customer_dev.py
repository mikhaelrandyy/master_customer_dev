from fastapi import APIRouter, status, HTTPException, Request

from schemas.customer_dev_sch import (CustomerDevSch, CustomerDevCreateSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, create_response)
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

@router.get("/business/{business_id}", response_model=GetResponseBaseSch[CustomerDevSch])
async def get_by_business_id(business_id: str):

    obj = await crud.customer_dev.get_by_business_id(business_id=business_id)

    if obj is None:
        raise IdNotFoundException(CustomerDev, business_id)
    
    return create_response(data=obj)

@router.post("", response_model=PostResponseBaseSch[list[CustomerDevSch]], status_code=status.HTTP_201_CREATED)
async def create(request: Request, sch: list[CustomerDevCreateSch]):
    
    """Create a new object"""
    if hasattr(request.state, 'login_user'):
        login_user=request.state.login_user

    obj = await crud.customer_dev.create(sch=sch, created_by=login_user.client_id)
    response_obj = await crud.customer_dev.get_by_ids(ids=[cust.id for cust in obj], is_active=True)
    return create_response(data=response_obj)

@router.put("/{id}", response_model=PostResponseBaseSch[CustomerDevSch], status_code=status.HTTP_201_CREATED)
async def update(id: str, request: Request, update_data: dict):
    
    if hasattr(request.state, 'login_user'):
        login_user = request.state.login_user

    obj_current = await crud.customer_dev.get(id=id)

    if not obj_current:
        raise HTTPException(status_code=404, detail=f"Customer tidak ditemukan")

    obj_updated = await crud.customer_dev.update_customer_dev(obj_current=obj_current, obj_new=update_data, updated_by=login_user.client_id)
    response_obj = await crud.customer_dev.get_by_id(id=obj_updated.id, is_active=True)
    return create_response(data=response_obj)