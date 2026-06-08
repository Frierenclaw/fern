from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from api import base_api_router
from core.config import TORTOISE_ORM, config

app = FastAPI(
    title=config.ENGINE_NAME,
    version=config.ENGINE_VERSION
)

register_tortoise(app,
                  TORTOISE_ORM)

app.include_router(base_api_router)
