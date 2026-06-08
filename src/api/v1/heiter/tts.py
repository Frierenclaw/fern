from dataclasses import dataclass

import httpx
from loguru import logger
from pipecat.frames.frames import ErrorFrame, TTSAudioRawFrame
from pipecat.services.settings import TTSSettings
from pipecat.services.tts_service import TTSService

from core.config import config


@dataclass
class HeiterTTSSettings(TTSSettings):
    pass 

class HeiterTTSService(TTSService):
    Settings = HeiterTTSSettings

    def __init__(
        self, 
        base_url: str = 'http://localhost:8000/v1/audio/speech', 
        model: str = 'edge_tts',
        voice: str = 'ru-RU-DmitryNeural',
        language: str = 'ru',
        **kwargs
    ):
        self.settings = self.Settings(model=model, voice=voice, language=language)
        super().__init__(settings=self.settings, **kwargs)
        self.base_url = base_url

    async def run_tts(self, text: str, *args, **kwargs):
        payload = {
            'model': self.settings.model,
            'input': text,
            'voice': self.settings.voice
        }
        
        try:
            timeout = httpx.Timeout(30.0, connect=5.0)
            async with (
                httpx.AsyncClient(timeout=timeout) as client,
                client.stream('POST', self.base_url, json=payload,
                            headers={'Authorization': f'Bearer {config.HEITER_TOKEN}'}) as response,
            ):
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f'Heiter TTS error: {error_text}')
                        
                    yield ErrorFrame(f'Heiter TTS error: {response.status_code}')
                    return

                chunk_count = 0
                async for chunk in response.aiter_bytes(chunk_size=1024):
                    chunk_count += 1
                    
                    yield TTSAudioRawFrame(
                        audio=chunk, 
                        sample_rate=16000,
                        num_channels=1
                    )
                        
        except Exception as e:
            yield ErrorFrame(f'Heiter TTS failed: {e}')