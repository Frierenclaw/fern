from utils.show_splash import show_splash
from utils.login import login_pipeline
from queue import Queue
from core.config import config

from voice_recognition.layer import VoiceRecognition
from vad.layer import VADLayer 

from loguru import logger

import io
import pyaudio
import numpy as np
import sounddevice as sd
import soundfile as sf
#! TODO СНЕСТИ ВЕСЬ КОД НАФИГ
print(sd.query_devices())
p = pyaudio.PyAudio()
stream = p.open(
                output_device_index=6,
                format=p.get_format_from_width(2),
                channels=1,
                rate=24000,
                output=True)

def mp3_to_pcm(mp3_bytes: bytes) -> bytes:
    buf = io.BytesIO(mp3_bytes)
    data, samplerate = sf.read(buf, dtype='int16')
    return data.tobytes()

def main():
    #show_splash()

    heiter = login_pipeline()

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
                        device=7, blocksize=BLOCKSIZE): # TODO: добавить в config выбор девайса
        
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
                        
                        voice_segments = VoiceRecognition.transcribe_audio(full_speech)
                        print(voice_segments)
                        if True:
                            print('Да, получено')
                            gpt_text = heiter.generate_message(voice_segments)
                            print(gpt_text)
                            for i in heiter.synthezis_text(gpt_text):
                                stream.write(mp3_to_pcm(i))
                            
if __name__ == '__main__':
    main()