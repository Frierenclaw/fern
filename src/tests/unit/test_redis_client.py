"""
Unit tests for redis_db.client.RedisClient.
"""
from __future__ import annotations

import uuid

import pytest

from redis_db.client import RedisClient


def _make_redis_client(fake_redis) -> RedisClient:
    return RedisClient(fake_redis)


class TestGetCharacter:
    @pytest.mark.asyncio
    async def test_returns_none_when_missing(self, fake_redis):
        rc = _make_redis_client(fake_redis)
        assert await rc.get_character(str(uuid.uuid4())) is None

    @pytest.mark.asyncio
    async def test_returns_stored_data(self, fake_redis):
        import orjson
        rc = _make_redis_client(fake_redis)
        cid = str(uuid.uuid4())
        data = {"id": cid, "name": "Frieren"}
        await fake_redis.set(f"hub:character:{cid}", orjson.dumps(data))
        result = await rc.get_character(cid)
        assert result["name"] == "Frieren"


class TestStoreCharacter:
    @pytest.mark.asyncio
    async def test_stores_character(self, fake_redis):
        from api.v1.schemas.base_dtos import CharacterDTO, UserDTO

        rc = _make_redis_client(fake_redis)
        cid = str(uuid.uuid4())
        dto = CharacterDTO(
            id=uuid.uuid4(), name="Frieren", description="Mage",
            cover_url=None, model_url=None,
            created_by=UserDTO(id=uuid.uuid4(), full_name="Author"),
        )
        await rc.store_character(cid, dto, ttl=3600)
        stored = await fake_redis.get(f"hub:character:{cid}")
        assert stored is not None


class TestLikeCharacter:
    @pytest.mark.asyncio
    async def test_adds_like(self, fake_redis):
        rc = _make_redis_client(fake_redis)
        cid = str(uuid.uuid4())
        uid = str(uuid.uuid4())
        await rc.like_character(cid, uid)
        count = await rc.get_character_likes(cid)
        assert count == 1

    @pytest.mark.asyncio
    async def test_duplicate_like_count_stays_one(self, fake_redis):
        rc = _make_redis_client(fake_redis)
        cid = str(uuid.uuid4())
        uid = str(uuid.uuid4())
        await rc.like_character(cid, uid)
        await rc.like_character(cid, uid)
        count = await rc.get_character_likes(cid)
        assert count == 1


class TestUnlikeCharacter:
    @pytest.mark.asyncio
    async def test_removes_like(self, fake_redis):
        rc = _make_redis_client(fake_redis)
        cid = str(uuid.uuid4())
        uid = str(uuid.uuid4())
        await rc.like_character(cid, uid)
        await rc.unlike_character(cid, uid)
        count = await rc.get_character_likes(cid)
        assert count == 0


class TestGetCharacterLikes:
    @pytest.mark.asyncio
    async def test_empty_likes(self, fake_redis):
        rc = _make_redis_client(fake_redis)
        assert await rc.get_character_likes(str(uuid.uuid4())) == 0

    @pytest.mark.asyncio
    async def test_multiple_likes(self, fake_redis):
        rc = _make_redis_client(fake_redis)
        cid = str(uuid.uuid4())
        for _ in range(3):
            await rc.like_character(cid, str(uuid.uuid4()))
        assert await rc.get_character_likes(cid) == 3
