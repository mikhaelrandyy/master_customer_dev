from fastapi import APIRouter, status, Depends, UploadFile, HTTPException, Response

from schemas.customer_dev_sch import (CustomerDevSch, CustomerDevCreateSch, CustomerDevByIdSch, CustomerDevByIdIncludeBidangSch)
from schemas.response_sch import (PostResponseBaseSch, GetResponseBaseSch, GetResponsePaginatedSch, PutResponseBaseSch, create_response)
# from services.customer_dev_service import CustomerDevService
from models import CustomerDev
from models.customer_dev_model import Worker
import crud

router = APIRouter()

@router.post("", response_model=PostResponseBaseSch[list[CustomerDevSch]], status_code=status.HTTP_201_CREATED)
async def create(sch: list[CustomerDevCreateSch]):
    
    """Create a new object"""

    obj = await crud.customer_dev.create(sch=sch)

    return create_response(data=obj)