from typing import Annotated

from fastapi import Depends

from api.v1.chat_logic import ChatLayer
from api.v1.deps.get_redis import get_redis
from redis_db import Redis as RedisDB


async def get_chat_layer(redis: Annotated[RedisDB, Depends(get_redis)]) -> ChatLayer:
    return ChatLayer(redis)
