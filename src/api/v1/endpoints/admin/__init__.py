from fastapi import APIRouter

from api.v1.endpoints.admin import hub, user

base_admin_router = APIRouter(prefix='/admin')
base_admin_router.include_router(user.base_user_router)
base_admin_router.include_router(hub.base_admin_hub_router)