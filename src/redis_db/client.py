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

    async def invalidate_character(self,
                                   character_id: str):
        return await self.redis_client.unlink(f'hub:character:{character_id}')
    
    async def get_character_likes(self,
                                  character_id: str):
        return await self.redis_client.zcard(f'likes:character:{character_id}')

    def _chat_key(self, chat_id: str) -> str:
        return f'chat:{chat_id}'

    def _messages_key(self, chat_id: str) -> str:
        return f'chat:{chat_id}:messages'

    async def create_chat(self,
                          user_id: str,
                          character_id: str,
                          chat_id: str,
                          ttl: int = 604800):
        return await self.redis_client.set(self._chat_key(chat_id),
                                           orjson.dumps({'character_id': character_id,
                                                         'user_id': user_id}),
                                           ex=ttl)

    async def get_chat(self,
                       chat_id: str) -> dict | None:
        data = await self.redis_client.get(self._chat_key(chat_id))

        if not data:
            return None

        return orjson.loads(data)

    async def get_messages(self,
                           chat_id: str) -> list[dict]:
        """
        Cached sliding window, oldest message first
        """
        raw_messages = await self.redis_client.lrange(self._messages_key(chat_id), 0, -1)

        return [orjson.loads(raw_message) for raw_message in raw_messages]

    async def append_message(self,
                             chat_id: str,
                             message: dict,
                             window_size: int,
                             ttl: int = 604800):
        """
        Push one message into the window and drop everything older than `window_size`
        """
        key = self._messages_key(chat_id)

        async with self.redis_client.pipeline(transaction=True) as pipe:
            pipe.rpush(key, orjson.dumps(message))
            pipe.ltrim(key, -window_size, -1)
            pipe.expire(key, ttl)

            return await pipe.execute()

    async def store_messages(self,
                             chat_id: str,
                             messages: list[dict],
                             window_size: int,
                             ttl: int = 604800):
        """
        Rebuild the window cache from the db, oldest message first
        """
        key = self._messages_key(chat_id)

        async with self.redis_client.pipeline(transaction=True) as pipe:
            pipe.delete(key)

            if messages:
                pipe.rpush(key, *[orjson.dumps(message) for message in messages])
                pipe.ltrim(key, -window_size, -1)
                pipe.expire(key, ttl)

            return await pipe.execute()

    async def invalidate_chat(self,
                              chat_id: str):
        return await self.redis_client.unlink(self._chat_key(chat_id),
                                              self._messages_key(chat_id))
