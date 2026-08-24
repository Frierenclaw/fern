"""
Unit tests for api.v1.chat_logic.layer.ChatLayer: db log + redis sliding window.
"""
from __future__ import annotations

import uuid

import pytest
from tortoise import Tortoise

from api.v1.chat_logic import ChatLayer
from models.chat import Chat, Message
from models.enums.message_role import MessageRoleEnum
from redis_db.client import RedisClient


@pytest.fixture
async def db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["models.user", "models.character",
                            "models.character_collection", "models.client", "models.chat"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def character(db):
    from models.character import Character
    from models.user import User

    user = await User.create(full_name="Fern", email=f"{uuid.uuid4()}@test.com",
                             password=b"hash")
    character = await Character.create(name="Frieren", description="mage",
                                       prompt="You are Frieren", created_by=user)
    return character


def _make_layer(fake_redis, window_size: int = 5) -> ChatLayer:
    return ChatLayer(RedisClient(fake_redis), window_size=window_size, ttl=60)


class TestCreate:
    @pytest.mark.asyncio
    async def test_creates_row_and_caches_meta(self, fake_redis, character):
        layer = _make_layer(fake_redis)

        chat = await layer.create(user_id=character.created_by_id,
                                  character_id=character.id)

        assert await Chat.filter(id=chat.id).exists()
        assert await layer.get_chat(chat.id) == {
            "user_id": str(character.created_by_id),
            "character_id": str(character.id),
        }

    @pytest.mark.asyncio
    async def test_get_chat_falls_back_to_db(self, fake_redis, character):
        layer = _make_layer(fake_redis)
        chat = await layer.create(user_id=character.created_by_id,
                                  character_id=character.id)

        await fake_redis.flushall()

        assert await layer.get_chat(chat.id) == {
            "user_id": str(character.created_by_id),
            "character_id": str(character.id),
        }

    @pytest.mark.asyncio
    async def test_get_chat_returns_none_when_missing(self, fake_redis, db):
        layer = _make_layer(fake_redis)

        assert await layer.get_chat(uuid.uuid4()) is None


class TestSlidingWindow:
    @pytest.mark.asyncio
    async def test_window_is_capped_but_log_is_not(self, fake_redis, character):
        layer = _make_layer(fake_redis, window_size=5)
        chat = await layer.create(user_id=character.created_by_id,
                                  character_id=character.id)

        await layer.get_window(chat.id) # Warm the cache before appending

        for i in range(12):
            await layer.append(chat.id, MessageRoleEnum.USER, f"msg-{i}")

        window = await layer.get_window(chat.id)

        assert len(window) == 5
        assert [m["content"] for m in window] == [f"msg-{i}" for i in range(7, 12)]
        assert await Message.filter(chat_id=chat.id).count() == 12

    @pytest.mark.asyncio
    async def test_window_is_rebuilt_from_db_on_cache_miss(self, fake_redis, character):
        layer = _make_layer(fake_redis, window_size=3)
        chat = await layer.create(user_id=character.created_by_id,
                                  character_id=character.id)

        await layer.get_window(chat.id)

        for i in range(6):
            role = MessageRoleEnum.USER if i % 2 == 0 else MessageRoleEnum.ASSISTANT
            await layer.append(chat.id, role, f"msg-{i}")

        await fake_redis.delete(f"chat:{chat.id}:messages")

        window = await layer.get_window(chat.id)

        assert [m["content"] for m in window] == ["msg-3", "msg-4", "msg-5"]
        assert [m["role"] for m in window] == ["assistant", "user", "assistant"]

    @pytest.mark.asyncio
    async def test_empty_chat_has_empty_window(self, fake_redis, character):
        layer = _make_layer(fake_redis)
        chat = await layer.create(user_id=character.created_by_id,
                                  character_id=character.id)

        assert await layer.get_window(chat.id) == []
