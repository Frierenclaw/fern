from fastapi import Request
from redis.asyncio import Redis


async def get_pure_redis(request: Request) -> Redis:
    return request.app.state.redis