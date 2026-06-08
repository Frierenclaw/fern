"""
created by hereuknow, in 2026
hereuknow.ru

Authentication layer: JWT token generation/decoding and password hashing via bcrypt
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

import bcrypt
import jwt

from api.v1.auth_logic.errors import UnsupportedTokenTypeError
from core.config import config


class Auth:
    """
    An jwt-auth layer
    """

    @staticmethod
    def _make_token(token_type: Literal['access', 'refresh'],
                    payload: dict) -> str:
        if token_type not in ('access', 'refresh'):
            raise UnsupportedTokenTypeError
        
        pvk_dict = {'access': config.ACCESS_PRIVATE_KEY,
                    'refresh': config.REFRESH_PRIVATE_KEY}
        
        token = jwt.encode(
            payload=payload,
            key=pvk_dict.get(token_type),
            algorithm=config.JWT_ALGO
        )

        return token
    
    @staticmethod
    def _decode_token(token_type: Literal['access', 'refresh'],
                     token: str):
        if token_type not in ('access', 'refresh'):
            raise UnsupportedTokenTypeError
        
        pbk_dict = {'access': config.ACCESS_PUBLIC_KEY,
                    'refresh': config.REFRESH_PUBLIC_KEY}
        
        decoded_token = jwt.decode(jwt=token,
                                   key=pbk_dict.get(token_type),
                                   algorithms=[config.JWT_ALGO])
        
        return decoded_token

    @classmethod
    def generate_access_token(
        cls,
        user_id: UUID
    ):
        dt_now_utc = datetime.now(UTC)

        payload = {
            'user_id': str(user_id),
            'iat': dt_now_utc,
            'exp': dt_now_utc + timedelta(seconds=config.ACCESS_TOKEN_TTL)
        }

        token = cls._make_token('access',
                                payload)
        
        return token
    
    @classmethod
    def generate_refresh_token(
        cls,
        user_id: UUID
    ):
        dt_now_utc = datetime.now(UTC)
        jti = uuid4()

        payload = {
            'jti': str(jti),
            'user_id': str(user_id),
            'iat': dt_now_utc,
            'exp': dt_now_utc + timedelta(seconds=config.REFRESH_TOKEN_TTL)
        }

        token = cls._make_token('refresh',
                                payload)
        
        return token
    
    @classmethod
    def decode_access_token(cls,
                            token: str):
        decoded_token = cls._decode_token('access',
                                  token)
        
        return decoded_token

    @classmethod
    def decode_refresh_token(cls,
                             token: str):
        decoded_token = cls._decode_token('refresh',
                                  token)
        
        return decoded_token
    
    @classmethod
    async def hash_password(cls, password: str) -> bytes:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return await asyncio.to_thread(bcrypt.hashpw, 
                                       password=password_bytes, 
                                       salt=salt)

    @classmethod
    async def check_password(cls, hashed_password: bytes, inputed_password: str) -> bool:
        password_bytes = inputed_password.encode('utf-8')
        return await asyncio.to_thread(
            bcrypt.checkpw, 
            password=password_bytes, 
            hashed_password=hashed_password
        )