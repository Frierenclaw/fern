from faster_whisper import WhisperModel
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.whisper.stt import WhisperSTTService

_whisper_model = WhisperModel("base", device="cpu", compute_type="int8")


def create_stt() -> WhisperSTTService:
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            model="base",
        ),
    )
    stt._model = _whisper_model
    return stt


def create_vad() -> SileroVADAnalyzer:
    return SileroVADAnalyzer()

