from fastapi import APIRouter

from api.v1.endpoints.admin.hub import delete, update

base_admin_hub_router = APIRouter(prefix='/hub')
base_admin_hub_router.include_router(delete.router)
base_admin_hub_router.include_router(update.router)