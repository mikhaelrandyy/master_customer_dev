from fastapi import APIRouter, Depends
from configs.permission import Permission
# from routes.endpoints import customer, debtor, unit_customer,customer_doc

api_router = APIRouter(dependencies=[Depends(Permission().get_login_user)])