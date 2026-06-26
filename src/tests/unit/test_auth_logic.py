"""
Unit tests for api.v1.auth_logic.layer.Auth – JWT encode/decode and bcrypt.
"""
from __future__ import annotations

import uuid

import pytest

from api.v1.auth_logic import Auth
from api.v1.auth_logic.errors import UnsupportedTokenTypeError


class TestMakeToken:
    def test_access_token_is_string(self):
        token = Auth._make_token("access", {"sub": "1"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_refresh_token_is_string(self):
        token = Auth._make_token("refresh", {"sub": "1"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_invalid_token_type_raises(self):
        with pytest.raises(UnsupportedTokenTypeError):
            Auth._make_token("invalid", {})


class TestDecodeToken:
    def test_round_trip_access(self):
        payload = {"user_id": str(uuid.uuid4()), "iat": 0, "exp": 9999999999}
        token = Auth._make_token("access", payload)
        decoded = Auth._decode_token("access", token)
        assert decoded["user_id"] == payload["user_id"]

    def test_round_trip_refresh(self):
        payload = {"jti": str(uuid.uuid4()), "user_id": str(uuid.uuid4()), "iat": 0, "exp": 9999999999}
        token = Auth._make_token("refresh", payload)
        decoded = Auth._decode_token("refresh", token)
        assert decoded["jti"] == payload["jti"]
        assert decoded["user_id"] == payload["user_id"]

    def test_decode_with_wrong_key_fails(self):
        token = Auth._make_token("access", {"user_id": "x"})
        with pytest.raises(Exception):
            Auth._decode_token("refresh", token)

    def test_invalid_token_type_raises(self):
        with pytest.raises(UnsupportedTokenTypeError):
            Auth._decode_token("bad", "tok")


class TestGenerateAccessToken:
    def test_contains_user_id(self):
        uid = uuid.uuid4()
        token = Auth.generate_access_token(uid)
        decoded = Auth.decode_access_token(token)
        assert decoded["user_id"] == str(uid)

    def test_has_iat_and_exp(self):
        token = Auth.generate_access_token(uuid.uuid4())
        decoded = Auth.decode_access_token(token)
        assert "iat" in decoded
        assert "exp" in decoded
        assert decoded["exp"] > decoded["iat"]


class TestGenerateRefreshToken:
    def test_contains_jti_and_user_id(self):
        uid = uuid.uuid4()
        token = Auth.generate_refresh_token(uid)
        decoded = Auth.decode_refresh_token(token)
        assert decoded["user_id"] == str(uid)
        assert "jti" in decoded
        uuid.UUID(decoded["jti"])

    def test_has_iat_and_exp(self):
        token = Auth.generate_refresh_token(uuid.uuid4())
        decoded = Auth.decode_refresh_token(token)
        assert "iat" in decoded
        assert "exp" in decoded


class TestPasswordHashing:
    @pytest.mark.asyncio
    async def test_hash_returns_bytes(self):
        h = await Auth.hash_password("secret")
        assert isinstance(h, bytes)

    @pytest.mark.asyncio
    async def test_check_correct_password(self):
        h = await Auth.hash_password("secret")
        assert await Auth.check_password(h, "secret") is True

    @pytest.mark.asyncio
    async def test_check_wrong_password(self):
        h = await Auth.hash_password("secret")
        assert await Auth.check_password(h, "wrong") is False

    @pytest.mark.asyncio
    async def test_different_hashes_for_same_password(self):
        h1 = await Auth.hash_password("pass")
        h2 = await Auth.hash_password("pass")
        assert h1 != h2
