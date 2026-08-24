from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from livekit import api as lk_api
from openai import AsyncOpenAI
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.deepgram.stt import DeepgramSTTService
from redis.asyncio import Redis as RedisClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.config import config
from redis_db import Redis as RedisDB


def create_stt() -> DeepgramSTTService:
    return DeepgramSTTService(
        api_key=config.DEEPGRAM_API_KEY,
        settings=DeepgramSTTService.Settings(
            model=config.DEEPGRAM_MODEL,
            language='multi',
            smart_format=True,
            profanity_filter=False,
            numerals=True,
            endpointing=100,
            keyterm=[
                'Frieren', 'FrierenClaw', 'LiveKit', 'Tortoise', 'aiogram', 'pipecat', 'Cartesia', 'VRM',
                'Фрирен'
            ],
        ),
    )


def create_vad() -> SileroVADAnalyzer:
    return SileroVADAnalyzer()

def user_or_ip(request: Request) -> str:
    """
    Rate limit key: authenticated user id when there is one, client IP otherwise
    """
    return getattr(request.state, 'user_id', None) or get_remote_address(request)


limiter = Limiter(key_func=user_or_ip,
                  storage_uri=f'redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_LIMITER_DB}')

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.livekit = lk_api.LiveKitAPI(url=config.LIVEKIT_API_URL,
                            api_key=config.LIVEKIT_API_KEY,
                            api_secret=config.LIVEKIT_API_SECRET) # Because we need active event loop for creating aiohttp instance
    app.state.redis = RedisClient(host=config.REDIS_HOST,
                              port=config.REDIS_PORT,
                              decode_responses=True,
                              password=config.REDIS_PASSWORD)
    app.state.redis_db = RedisDB(app.state.redis)
    app.state.openai = AsyncOpenAI(api_key=config.HEITER_TOKEN,
                                   base_url=config.HEITER_BASE_URL)
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    
    yield 
    
    await app.state.livekit.aclose()
    await app.state.redis.close()
