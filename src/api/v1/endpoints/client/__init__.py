from fastapi import APIRouter

from api.v1.endpoints.client import register

base_client_router = APIRouter(prefix='/client')
base_client_router.include_router(register.router)