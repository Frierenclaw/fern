"""
Chat history layer

The full log lives in Postgres (models.chat.Message), the sliding window that is
actually sent to the model is cached in Redis as a capped list
"""

from uuid import UUID

from loguru import logger

from core.config import config
from models.chat import Chat, Message
from models.enums.message_role import MessageRoleEnum
from redis_db import Redis as RedisDB


class ChatLayer:
    """
    Chat meta + message history with a sliding context window
    """

    def __init__(self,
                 redis: RedisDB,
                 window_size: int | None = None,
                 ttl: int | None = None):
        self.redis = redis
        self.window_size = window_size or config.CHAT_WINDOW_SIZE
        self.ttl = ttl or config.CHAT_TTL

    async def create(self,
                     user_id: UUID,
                     character_id: UUID) -> Chat:
        chat = await Chat.create(user_id=user_id,
                                 character_id=character_id)

        try:
            await self.redis.create_chat(chat_id=str(chat.id),
                                         user_id=str(user_id),
                                         character_id=str(character_id),
                                         ttl=self.ttl)
        except Exception as e: # Cache only, get_chat falls back to the db
            logger.warning(f'Cannot cache chat {chat.id}. Detail: {e}')

        return chat

    async def get_chat(self,
                       chat_id: UUID) -> dict | None:
        """
        Chat meta ({'user_id', 'character_id'}) from cache, with a db fallback
        """
        chat = await self.redis.get_chat(str(chat_id))

        if chat:
            return chat

        chat_row = await Chat.get_or_none(id=chat_id)

        if not chat_row:
            return None

        chat = {'user_id': str(chat_row.user_id),
                'character_id': str(chat_row.character_id)}

        try:
            await self.redis.create_chat(chat_id=str(chat_id),
                                         ttl=self.ttl,
                                         **chat)
        except Exception as e:
            logger.warning(f'Cannot cache chat {chat_id}. Detail: {e}')

        return chat

    async def get_window(self,
                         chat_id: UUID) -> list[dict]:
        """
        Last `window_size` messages as openai-style dicts, oldest first.
        Redis first, db on a cache miss
        """
        cached_window = await self.redis.get_messages(str(chat_id))

        if cached_window:
            return cached_window

        messages = await Message.filter(chat_id=chat_id) \
                                .order_by('-id') \
                                .limit(self.window_size)

        window = [{'role': message.role.value, 'content': message.content}
                  for message in reversed(messages)]

        if window:
            await self.redis.store_messages(chat_id=str(chat_id),
                                            messages=window,
                                            window_size=self.window_size,
                                            ttl=self.ttl)

        return window

    async def append(self,
                     chat_id: UUID,
                     role: MessageRoleEnum,
                     content: str) -> Message:
        """
        Write a message to the log and push it into the window cache.

        Must be called after get_window(), otherwise the cache may be cold and
        the window would end up holding only the messages of the current request
        """
        message = await Message.create(chat_id=chat_id,
                                       role=role,
                                       content=content)

        await self.redis.append_message(chat_id=str(chat_id),
                                        message={'role': role.value, 'content': content},
                                        window_size=self.window_size,
                                        ttl=self.ttl)

        return message
