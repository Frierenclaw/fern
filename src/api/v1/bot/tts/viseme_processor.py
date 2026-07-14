import json
from typing import Any

from loguru import logger
from pipecat.frames.frames import Frame, TTSTextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.livekit.transport import LiveKitTransport

from api.v1.bot.tts.cartesia import VRMVisemeFrame

CHAR_TO_VRM: dict[str, str] = {
    'a': 'aa',
    'o': 'oh',
    'u': 'ou',
    'e': 'ee',
    'i': 'ih',
    'а': 'aa',
    'о': 'oh',
    'у': 'ou',
    'е': 'ee',
    'и': 'ih',
    'э': 'ee',
    'ю': 'ou',
    'я': 'aa',
    'ё': 'aa',
}


def guess_viseme(word: str) -> str:
    for character in word.lower():
        if character in CHAR_TO_VRM:
            return CHAR_TO_VRM[character]
    return 'neutral'


class VRMVisemeProcessor(FrameProcessor):
    def __init__(
        self,
        transport: LiveKitTransport,
        *,
        word_fallback: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._transport = transport
        self._word_fallback = word_fallback

    async def _send_viseme(self, payload: dict[str, Any]) -> None:
        try:
            await self._transport.send_message(
                json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
            )
        except Exception as error:
            logger.error('[viseme] LiveKit send_message failed: {}', error)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, VRMVisemeFrame):
            duration_ms = round(max(0.03, frame.end_s - frame.start_s) * 1000)
            logger.debug(
                '[viseme] phoneme={!r} pts={} -> viseme={} duration={}ms',
                frame.phoneme,
                frame.pts,
                frame.viseme,
                duration_ms,
            )
            await self._send_viseme(
                {
                    'type': 'vrm_viseme',
                    'context_id': frame.context_id,
                    'phoneme': frame.phoneme,
                    'viseme': frame.viseme,
                    'duration_ms': duration_ms,
                }
            )

        elif self._word_fallback and isinstance(frame, TTSTextFrame):
            word = frame.text.strip()
            if word:
                viseme = guess_viseme(word)
                logger.debug(
                    '[viseme] fallback word={!r} pts={} -> viseme={}',
                    word,
                    frame.pts,
                    viseme,
                )
                await self._send_viseme(
                    {
                        'type': 'vrm_viseme',
                        'viseme': viseme,
                        'word': word,
                        'duration_ms': 100,
                    }
                )

        await self.push_frame(frame, direction)
