from pydantic_settings import BaseSettings
from faster_whisper import WhisperModel
from typing import Literal
from silero_vad import load_silero_vad

import socket

class Config(BaseSettings):
    WHISPER_MODEL_TYPE: Literal['small', 'medium'] = 'medium'
    WHISPER_DEVICE_TYPE: Literal['cpu', 'cuda'] = 'cpu'
    
    VR_SAMPLERATE: int = 16_000
    VR_CHANNELS: int = 1

config = Config()
whisper_model = WhisperModel(config.WHISPER_MODEL_TYPE,
                              device=config.WHISPER_DEVICE_TYPE, 
                              compute_type='int8' if config.WHISPER_DEVICE_TYPE == 'cpu' else 'float16')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

_vad = load_silero_vad()