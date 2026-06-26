"""
Unit tests for api.v1.heiter.tts.HeiterTTSService.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from api.v1.heiter.tts import HeiterTTSService


def _make_mock_client(response, stream_effect=None):
    """Build a mock httpx.AsyncClient that works with the TTS code's context manager pattern."""
    mock_stream_ctx = AsyncMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=response)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

    # stream() is a sync method on AsyncClient, must return ctx manager directly
    mock_stream = MagicMock(return_value=mock_stream_ctx)
    if stream_effect is not None:
        mock_stream.side_effect = stream_effect

    mock_client = MagicMock()
    mock_client.stream = mock_stream
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    return mock_client


class TestHeiterTTSService:
    def test_init(self):
        svc = HeiterTTSService(base_url="http://test:8000/v1/audio/speech")
        assert svc.base_url == "http://test:8000/v1/audio/speech"
        assert svc.settings.model == "edge_tts"

    @pytest.mark.asyncio
    async def test_run_tts_success(self):
        svc = HeiterTTSService(base_url="http://test:8000/v1/audio/speech")

        mock_response = AsyncMock()
        mock_response.status_code = 200

        async def fake_aiter_bytes(chunk_size=1024):
            yield b"audio_chunk_1"
            yield b"audio_chunk_2"

        mock_response.aiter_bytes = fake_aiter_bytes
        mock_client = _make_mock_client(mock_response)

        with patch("api.v1.heiter.tts.httpx.AsyncClient", return_value=mock_client):
            frames = []
            async for frame in svc.run_tts("Привет"):
                frames.append(frame)

        assert len(frames) == 2
        assert frames[0].audio == b"audio_chunk_1"
        assert frames[1].audio == b"audio_chunk_2"

    @pytest.mark.asyncio
    async def test_run_tts_error_response(self):
        svc = HeiterTTSService(base_url="http://test:8000/v1/audio/speech")

        mock_response = AsyncMock()
        mock_response.status_code = 500

        async def fake_aread():
            return b"internal error"

        mock_response.aread = fake_aread
        mock_client = _make_mock_client(mock_response)

        with patch("api.v1.heiter.tts.httpx.AsyncClient", return_value=mock_client):
            frames = []
            async for frame in svc.run_tts("Test"):
                frames.append(frame)

        assert len(frames) == 1
        assert "500" in frames[0].error

    @pytest.mark.asyncio
    async def test_run_tts_network_error(self):
        svc = HeiterTTSService(base_url="http://test:8000/v1/audio/speech")
        mock_client = _make_mock_client(None, stream_effect=httpx.ConnectError("refused"))

        with patch("api.v1.heiter.tts.httpx.AsyncClient", return_value=mock_client):
            frames = []
            async for frame in svc.run_tts("Test"):
                frames.append(frame)

        assert len(frames) == 1
        assert "failed" in frames[0].error.lower()
