import json

from pipecat.frames.frames import AggregatedTextProgressFrame, Frame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.livekit.transport import LiveKitTransport

CHAR_TO_VRM: dict[str, str] = {
    'a': 'aa', 'o': 'oh', 'u': 'ou',
    'e': 'ee', 'i': 'ih',
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

        if isinstance(frame, AggregatedTextProgressFrame):
            words = frame.accumulated_text.strip().split()
            if words:
                viseme = guess_viseme(words[-1])
                if viseme != 'neutral':
                    await self._transport.send_message(json.dumps({
                        'type': 'vrm_viseme',
                        'viseme': viseme,
                    }))

        await self.push_frame(frame, direction)