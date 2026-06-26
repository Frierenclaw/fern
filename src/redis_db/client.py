import time

import orjson
from redis import Redis

from api.v1.schemas.base_dtos import CharacterDTO


class RedisClient:
    """
    An Redis client
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get_character(self, character_id: str):
        data = await self.redis_client.get(f'hub:character:{character_id}')

        if not data:
            return None
        
        serialized_data = orjson.loads(data)

        return serialized_data

    async def store_character(self,
                              character_id: str,
                              character: CharacterDTO,
                              ttl: int = 3600):
        return await self.redis_client.set(name=f'hub:character:{character_id}',
                                      value=character.model_dump_json(),
                                      ex=ttl)
    
    async def like_character(self,
                             character_id: str,
                             user_id: str):
        return await self.redis_client.zadd(f'likes:character:{character_id}', {str(user_id): time.time()})
    
    async def unlike_character(self,
                               character_id: str,
                               user_id: str):
        return await self.redis_client.zrem(f'likes:character:{character_id}', str(user_id))
    
    async def get_character_likes(self,
                                  character_id: str):
        return await self.redis_client.zcard(f'likes:character:{character_id}')