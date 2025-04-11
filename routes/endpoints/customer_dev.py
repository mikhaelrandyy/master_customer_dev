from fastapi import APIRouter, status, HTTPException, Request, Depends
from sqlmodel import select, or_, func
from sqlalchemy.orm import selectinload
from fastapi_pagination import Params
from schemas.customer_dev_sch import (CustomerDevSch, CustomerDevCreateSch, CustomerDevByIdSch, ChangeDataSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, GetResponsePaginatedSch, create_response)
from models.customer_dev_model import CustomerDev
from services.pubsub_service import PubSubService
import crud
from utils.exceptions.common_exception import IdNotFoundException

router = APIRouter()

@router.post("", response_model=PostResponseBaseSch[list[CustomerDevSch]], status_code=status.HTTP_201_CREATED)
async def create(request: Request, sch: list[CustomerDevCreateSch]):
    
    """Create a new object"""
    if hasattr(request.state, 'login_user'):
        login_user=request.state.login_user
    objs = await crud.customer_dev.create_bulk(sch=sch, created_by=login_user.client_id)
    for obj in objs:
        customerdev_current = await crud.customer_dev.get_by_id(id=obj["id"])
        customerdev_current = CustomerDevByIdSch.model_validate(customerdev_current)
        mapping_cust_group = await crud.customer_dev_group.get_multi_by_reference_id(id=customerdev_current.id)
        PubSubService().publish_to_pubsub(topic_name="master-customerdev", message=customerdev_current, action="create")
        for map_obj in mapping_cust_group:
            PubSubService().publish_to_pubsub(topic_name="master-customerdevgroup", message=map_obj, action="create")

    return create_response(data=objs)

@router.put("/{id}", response_model=PostResponseBaseSch[CustomerDevSch], status_code=status.HTTP_201_CREATED)
async def update(id: str, request: Request, update_data: ChangeDataSch):
    
    if hasattr(request.state, 'login_user'):
        login_user = request.state.login_user

    obj_current = await crud.customer_dev.get(id=id)

    if not obj_current:
        raise HTTPException(status_code=404, detail=f"Customer tidak ditemukan")

    obj_updated = await crud.customer_dev.update_change_data(obj_current=obj_current, obj_new=update_data, updated_by=login_user.client_id)
    customerdev_current = await crud.customer_dev.get_by_id(id=obj_updated.id)
    customerdev_current = CustomerDevByIdSch.model_validate(customerdev_current)
    mapping_cust_group = await crud.customer_dev_group.get_multi_by_reference_id(id=id)
    PubSubService().publish_to_pubsub(topic_name="master-customerdev", message=customerdev_current, action="update")
    for map_obj in mapping_cust_group:
        PubSubService().publish_to_pubsub(topic_name="master-customerdevgroup", message=map_obj, action="update")
    
    return create_response(data=obj_updated)

@router.get("", response_model=GetResponsePaginatedSch[CustomerDevSch])
async def get_list(search: str | None = None, params: Params=Depends()):

    query = select(CustomerDev)

    if search:
        query = query.filter(
            or_(
                CustomerDev.code.ilike(f'%{search}%'),
                CustomerDev.first_name.ilike(f'%{search}%'),
                CustomerDev.last_name.ilike(f'%{search}%'),
                func.concat(CustomerDev.first_name, ' ', CustomerDev.last_name).ilike(f'%{search}%')
            )
        )

    objs = await crud.customer_dev.get_multi_paginated_ordered(query=query, params=params)

    return create_response(data=objs)

@router.get("/no-page", response_model=GetResponseBaseSch[list[CustomerDevSch]])
async def get_no_page():

    query = select(CustomerDev)

    objs = await crud.customer_dev.get_all_ordered(query=query, order_by="created_at")

    return create_response(data=objs)

@router.get("/{id}", response_model=GetResponseBaseSch[CustomerDevByIdSch])
async def get_by_id(id: str):

    obj = await crud.customer_dev.get_by_id(id=id)

    if obj is None:
        raise IdNotFoundException(CustomerDev, id)
    
    return create_response(data=obj)

@router.get("/business/{business_id}", response_model=GetResponseBaseSch[CustomerDevByIdSch])
async def get_by_business_id(business_id: str):

    obj = await crud.customer_dev.get_by_business_id(business_id=business_id)

    if obj is None:
        raise IdNotFoundException(CustomerDev, business_id)
    
    return create_response(data=obj)