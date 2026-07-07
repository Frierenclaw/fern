from fastapi import APIRouter

from api.v1.endpoints.admin.user import create, delete, edit, get

base_user_router = APIRouter(prefix='/user')
base_user_router.include_router(create.router)
base_user_router.include_router(delete.router)
base_user_router.include_router(edit.router)
base_user_router.include_router(get.router)
