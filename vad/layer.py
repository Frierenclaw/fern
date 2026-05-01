from core.config import _vad
from silero_vad import get_speech_timestamps
from loguru import logger

import numpy as np
import torch

class VADLayer:
    """
    The main class for voice activity detector
    """

    @classmethod
    def _return_voiced_segments(cls):
        """
        Вернуть речевые сегменты (дока для себя)
        """

    @classmethod
    def check_voice_activity(cls, chunk):
        """
        Проверка активности голоса в конкретном фрагменте.
        
        Args:
            chunk (np.ndarray): Одиночный кусок аудио из очереди
        """
        audio_flat = chunk.flatten()

        audio_tensor = torch.from_numpy(audio_flat)

        timestamps = get_speech_timestamps(
            audio_tensor, 
            _vad, 
            sampling_rate=16000, 
            threshold=0.5, 
            min_speech_duration_ms=250, 
            min_silence_duration_ms=100
        )
        return timestamps
