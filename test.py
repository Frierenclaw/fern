import sounddevice as sd
import numpy as np
import torch
from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps

vad = load_silero_vad()
model = WhisperModel('small', device="cpu", compute_type="int8")

chunks = []
# ! ЕБАНЫЙ НЕДО-УЧЕБНЫЙ ГОВНОКОД!

def callback(indata, frames, time, status):
    chunks.append(indata.copy()) # Можно юзать в  check_voice_activity. Поставить как колбэк

while True:
    with sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=callback, device=1):
        sd.sleep(15000) # Возможно ли убрать sd.sleep? Думаю что да

    audio = np.concatenate(chunks, axis=0).flatten()

    # VAD: нужен torch.Tensor
    audio_tensor = torch.from_numpy(audio)

    

    timestamps = get_speech_timestamps(
        audio_tensor,
        vad,
        sampling_rate=16000,
        threshold=0.5,          # чувствительность (0.3–0.7)
        min_speech_duration_ms=250,
        min_silence_duration_ms=100,
    )

    if not timestamps:
        print("Речь не обнаружена")
    else:
        # В _return_voiced_segments!
        # Склеиваем только речевые сегменты
        speech_chunks = [audio[t['start']:t['end']] for t in timestamps]
        speech_audio = np.concatenate(speech_chunks)

        segments, info = model.transcribe(speech_audio, language="ru", beam_size=5)
        for segment in segments:
            print(segment.text)

        chunks.clear()