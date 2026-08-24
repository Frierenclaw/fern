from functools import cached_property
from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_URL: str

    HEITER_BASE_URL: str
    HEITER_MODEL_NAME: str
    HEITER_TOKEN: str

    HEITER_TTS_MODEL: str
    HEITER_TTS_VOICE: str
    HEITER_TTS_LANGUAGE: str
    
    ENGINE_VERSION: str
    ENGINE_NAME: str

    LIVEKIT_URL: str
    LIVEKIT_API_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str

    S3_ENDPOINT_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    BUCKET_NAME: str
    S3_REGION_NAME: str

    MAX_COVER_SIZE: int = 5 * 1024 * 1024
    ALLOWED_COVER_EXTENSIONS: list[str]
    ALLOWED_COVER_MIME_TYPES: list[str]

    MAX_MODEL_SIZE: int = 100 * 1024 * 1024
    ALLOWED_MODEL_EXTENSIONS: list[str]
    ALLOWED_MODEL_MIME_TYPES: list[str]

    MAX_ANIMATIONS_SIZE: int = 15 * 1024 * 1024
    ALLOWED_ANIMATIONS_EXTENSIONS: list[str]
    ALLOWED_ANIMATIONS_MIME_TYPES: list[str]

    ACCESS_TOKEN_TTL: int
    REFRESH_TOKEN_TTL: int
    JWT_ALGO: str

    ACCESS_PRIVATE_KEY_PATH: str = 'certs/access_private.pem'
    ACCESS_PUBLIC_KEY_PATH: str = 'certs/access_public.pem'
    REFRESH_PRIVATE_KEY_PATH: str = 'certs/refresh_private.pem'
    REFRESH_PUBLIC_KEY_PATH: str = 'certs/refresh_public.pem'

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_LIMITER_DB: int

    USE_CARTESIA: bool = False
    CARTESIA_MODEL: str | None = None
    CARTESIA_API_KEY: str | None = None
    CARTESIA_VOICE_ID: str | None = None

    DEEPGRAM_API_KEY: str
    DEEPGRAM_MODEL: str

    CHAT_WINDOW_SIZE: int = 20 # How many last messages are sent to the model
    CHAT_TTL: int = 60 * 60 * 24 * 7 # Lifetime of the redis chat cache
    CHAT_MAX_MESSAGE_LENGTH: int = 4096

    @cached_property
    def ACCESS_PRIVATE_KEY(self) -> str:
        return Path(self.ACCESS_PRIVATE_KEY_PATH).read_text()

    @cached_property
    def ACCESS_PUBLIC_KEY(self) -> str:
        return Path(self.ACCESS_PUBLIC_KEY_PATH).read_text()

    @cached_property
    def REFRESH_PRIVATE_KEY(self) -> str:
        return Path(self.REFRESH_PRIVATE_KEY_PATH).read_text()

    @cached_property
    def REFRESH_PUBLIC_KEY(self) -> str:
        return Path(self.REFRESH_PUBLIC_KEY_PATH).read_text()
    
    @cached_property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"    

config = Config()

TORTOISE_ORM = {
    'connections': {
        'default': config.DB_URL
    },

    'timezone': 'UTC',
    
    'apps': {
        'models': {
            'models': [
                'models.user',
                'models.character',
                'models.character_collection',
                'models.client',
                'models.chat'
            ],
            'migrations': 'models.migrations',
            'default_connection': 'default'
        }
    }
}