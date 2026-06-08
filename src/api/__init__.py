from fastapi import APIRouter

from api.v1 import base_v1_router

base_api_router = APIRouter(prefix='/api')
base_api_router.include_router(base_v1_router)