"""
Unit-test fixtures: FakeRedis, mock external clients.
"""
from __future__ import annotations

import fakeredis.aioredis
import pytest


@pytest.fixture
async def fake_redis():
    server = fakeredis.aioredis.FakeServer()
    client = fakeredis.aioredis.FakeRedis(server=server, decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture(autouse=True)
def _patch_redis_client(monkeypatch, fake_redis):
    """Replace the global redis_client singleton with FakeRedis."""
    import core.clients

    monkeypatch.setattr(core.clients, "RedisClient", lambda *a, **kw: fake_redis)


