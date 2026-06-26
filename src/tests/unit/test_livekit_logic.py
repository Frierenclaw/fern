"""
Unit tests for api.v1.livekit_logic.layer.LiveKIT.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.v1.livekit_logic.layer import LiveKIT


def _make_livekit() -> LiveKIT:
    mock_client = MagicMock()
    return LiveKIT(mock_client)


class TestCreateRoom:
    @pytest.mark.asyncio
    async def test_returns_room_name(self):
        lk = _make_livekit()
        mock_response = MagicMock()
        mock_response.name = "room_abc"
        lk.livekit.room.create_room = AsyncMock(return_value=mock_response)
        result = await lk.create_room("room_abc")
        assert result == "room_abc"
        lk.livekit.room.create_room.assert_called_once()


class TestCreateToken:
    def test_returns_jwt_string(self):
        token = LiveKIT.create_token("room_1", "user_1")
        assert isinstance(token, str)
        assert len(token) > 20
