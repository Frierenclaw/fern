from fastapi import APIRouter

from api.v1.endpoints.frieren_hub import create, delete, get, like, update

base_frieren_hub_router = APIRouter(prefix='/hub',
                                    tags=['Frieren hub (characters hub)'])

base_frieren_hub_router.include_router(create.router)
base_frieren_hub_router.include_router(get.router)
base_frieren_hub_router.include_router(update.router)
base_frieren_hub_router.include_router(delete.router)
base_frieren_hub_router.include_router(like.router)