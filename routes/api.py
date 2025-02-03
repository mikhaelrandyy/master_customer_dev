from fastapi import APIRouter, Depends
from routes.endpoints import customer_dev
from configs.permission import Permission

api_router = APIRouter(dependencies=[Depends(Permission().get_login_user)])

# api_router = APIRouter()

api_router.include_router(customer_dev.router, prefix="/customer-dev", tags=["customer_dev"])


