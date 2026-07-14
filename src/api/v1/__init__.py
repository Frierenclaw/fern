from fastapi import APIRouter

from api.v1.endpoints import admin, auth, client, frieren_hub, rooms

base_v1_router = APIRouter(prefix='/v1')

base_v1_router.include_router(auth.base_auth_router)
base_v1_router.include_router(rooms.base_rooms_router)
base_v1_router.include_router(frieren_hub.base_frieren_hub_router)
base_v1_router.include_router(admin.base_admin_router)
base_v1_router.include_router(client.base_client_router)