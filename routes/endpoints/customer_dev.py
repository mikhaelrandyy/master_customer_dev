from fastapi import APIRouter, status, HTTPException, Request, Depends
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload
from fastapi_pagination import Params
from schemas.customer_dev_sch import (CustomerDevSch, CustomerDevCreateSch, CustomerDevByIdSch, ChangeDataSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, GetResponsePaginatedSch, create_response)
from models.customer_dev_model import CustomerDev
import crud
from utils.exceptions.common_exception import IdNotFoundException

router = APIRouter()

@router.get("", response_model=GetResponsePaginatedSch[CustomerDevSch])
async def get_list(params: Params=Depends()):

    query = select(CustomerDev)

    objs = await crud.customer_dev.get_multi_paginated_ordered(query=query, params=params)

    return create_response(data=objs)

@router.get("/no-page", response_model=GetResponseBaseSch[list[CustomerDevSch]])
async def get_no_page():

    query = select(CustomerDev)

    objs = await crud.customer_dev.get_all_ordered(query=query, order_by="created_at")

    return create_response(data=objs)

@router.get("/{id}", response_model=GetResponseBaseSch[CustomerDevByIdSch])
async def get_by_id(id: str, is_active: bool | None = None):

    obj = await  crud.customer_dev.get_by_id(id=id, is_active=is_active)

    if obj is None:
        raise IdNotFoundException(CustomerDev, id)
    
    return create_response(data=obj)

@router.get("/business/{business_id}", response_model=GetResponseBaseSch[CustomerDevByIdSch])
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
    return create_response(data=obj)

@router.put("/{id}", response_model=PostResponseBaseSch[CustomerDevByIdSch], status_code=status.HTTP_201_CREATED)
async def update(id: str, request: Request, update_data: ChangeDataSch):
    
    if hasattr(request.state, 'login_user'):
        login_user = request.state.login_user

    obj_current = await crud.customer_dev.get(id=id)

    if not obj_current:
        raise HTTPException(status_code=404, detail=f"Customer tidak ditemukan")

    obj_updated = await crud.customer_dev.update_customer_dev(obj_current=obj_current, obj_new=update_data, updated_by=login_user.client_id)
    response_obj = await crud.customer_dev.get_by_id(id=obj_updated.id, is_active=True)
    return create_response(data=response_obj)