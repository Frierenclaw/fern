import json

from loguru import logger
from pipecat.frames.frames import Frame, TTSTextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.livekit.transport import LiveKitTransport

CHAR_TO_VRM: dict[str, str] = {
    'a': 'aa', 'o': 'oh', 'u': 'ou', 'e': 'ee', 'i': 'ih',
    'а': 'aa', 'о': 'oh', 'у': 'ou', 'е': 'ee', 'и': 'ih',
    'э': 'ee', 'ю': 'ou', 'я': 'aa', 'ё': 'aa',
}

def guess_viseme(word: str) -> str:
    for ch in word.lower():
        if ch in CHAR_TO_VRM:
            return CHAR_TO_VRM[ch]
    return 'neutral'


class VRMVisemeProcessor(FrameProcessor):
    def __init__(self, transport: LiveKitTransport, **kwargs):
        super().__init__(**kwargs)
        self._transport = transport

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TTSTextFrame):
            word = frame.text.strip()
            if word:
                viseme = guess_viseme(word)
                logger.debug('[viseme] word={!r} pts={} → viseme={}', word, frame.pts, viseme)
                if viseme != 'neutral':
                    try:
                        payload = json.dumps({
                            'type': 'vrm_viseme',
                            'viseme': viseme,
                            'word': word,
                        }).encode()
                        await self._transport._client.send_data(payload)
                    except Exception as e:
                        logger.error('[viseme] send_data failed: {}', e)

        await self.push_frame(frame, direction)

