from fastapi import APIRouter

from api.v1.endpoints.admin import user

base_admin_router = APIRouter(prefix='/admin')
base_admin_router.include_router(user.base_user_router)
