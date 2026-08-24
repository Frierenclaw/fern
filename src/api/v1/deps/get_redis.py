from fastapi import Request

from redis_db import Redis as RedisDB


async def get_redis(request: Request) -> RedisDB:
    return request.app.state.redis_db