from utils.show_splash import show_splash
from queue import Queue
from core.config import config

from voice_recognition.layer import VoiceRecognition
from vad.layer import VADLayer 

from loguru import logger

import numpy as np
import sounddevice as sd

def main():
    show_splash()

    queue = Queue()
    SAMPLERATE = config.VR_SAMPLERATE
    BLOCKSIZE = 512
    CHUNKS_PER_BUFFER = int(SAMPLERATE * 1.0 / BLOCKSIZE)

    speech_accumulator = []  
    silence_counter = 0
    SILENCE_THRESHOLD = 1

    def audio_callback(indata, frames, time, status):
        queue.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLERATE, channels=config.VR_CHANNELS,
                        dtype='float32', callback=audio_callback,
                        device=1, blocksize=BLOCKSIZE): # TODO: добавить в config выбор девайса
        
        logger.debug('Starting listening... Press CTRL + C for stop')

        buffer = []
        while True:
            chunk = queue.get()
            buffer.append(chunk)

            if len(buffer) < CHUNKS_PER_BUFFER:
                continue

            audio = np.concatenate(buffer, axis=0).flatten()
            buffer.clear()

            timestamps = VADLayer.check_voice_activity(audio)

            if timestamps:
                silence_counter = 0
                for ts in timestamps:
                    speech_accumulator.append(audio[ts['start']:ts['end']])
            else:
                if speech_accumulator:
                    silence_counter += 1

                    if silence_counter >= SILENCE_THRESHOLD:
                        full_speech = np.concatenate(speech_accumulator)
                        speech_accumulator.clear()
                        silence_counter = 0

                        logger.debug(f'Transcribing {len(full_speech)/SAMPLERATE:.2f}s of speech')
                        VoiceRecognition.transcribe_audio(full_speech)
if __name__ == '__main__':
    main()