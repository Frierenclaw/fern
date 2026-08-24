from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from api import base_api_router
from core.clients import lifespan
from core.config import TORTOISE_ORM, config

app = FastAPI(
    title=config.ENGINE_NAME,
    version=config.ENGINE_VERSION,
    lifespan=lifespan
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False, # All in the body
    allow_methods=['*'],
    allow_headers=['*'],
)

register_tortoise(app,
                  TORTOISE_ORM)

app.include_router(base_api_router)
