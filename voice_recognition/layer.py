from core.config import whisper_model

import numpy as np
from loguru import logger

class VoiceRecognition:
    @classmethod
    def concatenate_speech_segments(cls,
                                    audio,
                                    speech_timestamps):
        speech_chunks = [audio[timestamp['start']:timestamp['end']]
                        for timestamp in speech_timestamps]
        speech_audio = np.concatenate(speech_chunks)

        return speech_audio
    
    @classmethod
    def transcribe_audio(cls,
                         audio):
        segments, info = whisper_model.transcribe(audio, language='ru', beam_size=5)

        for segment in segments:
            if any(word in segment.text.lower() for word in ['гугле', 'гугл', 'гугал', 'google']):
                logger.debug(f'Wake word detected, segment text: {segment.text}')
            else:
                logger.debug(f'Voice segment detected, but no wake word. Segment text: {segment.text}')

        full_text = ' '.join(segment.text for segment in segments)
        print(full_text)
        return full_text