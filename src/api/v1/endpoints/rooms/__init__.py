from fastapi import APIRouter

from api.v1.endpoints.rooms import create

base_rooms_router = APIRouter(prefix='/room')

base_rooms_router.include_router(create.router)