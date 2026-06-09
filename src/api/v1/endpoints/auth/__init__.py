from fastapi import APIRouter

from api.v1.endpoints.auth import login, register

base_auth_router = APIRouter(prefix='/auth',
                             tags=['Auth'])

base_auth_router.include_router(login.router)
base_auth_router.include_router(register.router)