from fastapi import FastAPI
from faster_whisper import WhisperModel
from livekit import api as lk_api
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.whisper.stt import WhisperSTTService
from redis.asyncio import Redis as RedisClient

from core.config import config
from redis_db import Redis as RedisDB

_whisper_model = WhisperModel("base", device="cpu", compute_type="int8")


def create_stt() -> WhisperSTTService:
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            model="base",
            language="ru"
        ),
    )
    stt._model = _whisper_model
    return stt


def create_vad() -> SileroVADAnalyzer:
    return SileroVADAnalyzer()


async def lifespan(app: FastAPI):
    app.state.livekit = lk_api.LiveKitAPI(url=config.LIVEKIT_API_URL,
                            api_key=config.LIVEKIT_API_KEY,
                            api_secret=config.LIVEKIT_API_SECRET) # Because we need active event loop for creating aiohttp instance
    app.state.redis = RedisClient(host=config.REDIS_HOST,
                              port=config.REDIS_PORT,
                              decode_responses=True,
                              password=config.REDIS_PASSWORD)
    app.state.redis_db = RedisDB(app.state.redis)
    
    yield 
    
    await app.state.livekit.aclose()
    await app.state.redis.close()