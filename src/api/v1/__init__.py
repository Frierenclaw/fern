from fastapi import APIRouter

from api.v1.endpoints import auth, rooms

base_v1_router = APIRouter(prefix='/v1')

base_v1_router.include_router(auth.base_auth_router)
base_v1_router.include_router(rooms.base_rooms_router)