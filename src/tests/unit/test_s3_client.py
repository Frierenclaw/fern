"""
Unit tests for api.v1.s3.layer.S3Client.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestUploadObject:
    @pytest.mark.asyncio
    async def test_calls_put_object(self):
        with patch("api.v1.s3.layer.aioboto3.Session") as MockSession:
            mock_s3 = AsyncMock()
            mock_client_ctx = AsyncMock()
            mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_s3)
            mock_client_ctx.__aexit__ = AsyncMock(return_value=False)
            MockSession.return_value.client.return_value = mock_client_ctx

            from api.v1.s3.layer import S3Client
            s3 = S3Client()
            result = await s3.upload_object("cover.jpg", b"data", content_type="image/jpeg")

            mock_s3.put_object.assert_called_once()
            call_kwargs = mock_s3.put_object.call_args.kwargs
            assert call_kwargs["Bucket"] == "test-bucket"
            assert call_kwargs["Key"] == "cover.jpg"
            assert call_kwargs["ContentType"] == "image/jpeg"
            assert result == "https://s3.test.com/test-bucket/cover.jpg"

    @pytest.mark.asyncio
    async def test_omits_content_type_when_none(self):
        with patch("api.v1.s3.layer.aioboto3.Session") as MockSession:
            mock_s3 = AsyncMock()
            mock_client_ctx = AsyncMock()
            mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_s3)
            mock_client_ctx.__aexit__ = AsyncMock(return_value=False)
            MockSession.return_value.client.return_value = mock_client_ctx

            from api.v1.s3.layer import S3Client
            s3 = S3Client()
            await s3.upload_object("model.glb", b"data")

            call_kwargs = mock_s3.put_object.call_args.kwargs
            assert "ContentType" not in call_kwargs
