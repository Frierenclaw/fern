import base64
import json
import unicodedata
from dataclasses import dataclass
from typing import Any

from pipecat.frames.frames import (
    DataFrame,
    Frame,
    TTSAudioRawFrame,
    TTSStoppedFrame,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.utils.time import seconds_to_nanoseconds


@dataclass
class VRMVisemeFrame(DataFrame):
    context_id: str
    phoneme: str
    viseme: str
    start_s: float
    end_s: float


def phoneme_to_vrm(raw: str) -> str:
    phoneme = unicodedata.normalize('NFC', raw)
    for marker in ('ˈ', 'ˌ', 'ː', 'ʲ', 'ʷ'):
        phoneme = phoneme.replace(marker, '')

    if phoneme.startswith(('a', 'ɑ', 'æ', 'ɐ', 'ʌ')):
        return 'aa'
    if phoneme.startswith(('i', 'ɪ', 'ɨ', 'y', 'ʏ', 'j')):
        return 'ih'
    if phoneme.startswith(('u', 'ʊ', 'ɯ')):
        return 'ou'
    if phoneme.startswith(('e', 'ɛ', 'ə', 'ɘ', 'ɜ', 'ɤ')):
        return 'ee'
    if phoneme.startswith(('o', 'ɔ', 'ɒ', 'ɵ')):
        return 'oh'

    return 'neutral'


class VisemeCartesiaTTSService(CartesiaTTSService):
    VISEME_LEAD_NS = seconds_to_nanoseconds(0.03)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pending_viseme_frames: list[VRMVisemeFrame] = []

    def _build_msg(self, *args, **kwargs) -> str:
        message = json.loads(super()._build_msg(*args, **kwargs))
        message['add_phoneme_timestamps'] = True
        return json.dumps(message)

    async def _append_phoneme_timestamps(
        self,
        context_id: str,
        data: dict[str, Any],
    ) -> None:
        phonemes = data.get('phonemes', [])
        starts = data.get('start', [])
        ends = data.get('end', [])

        for phoneme, start, end in zip(phonemes, starts, ends, strict=False):
            await self.append_to_audio_context(
                context_id,
                VRMVisemeFrame(
                    context_id=context_id,
                    phoneme=str(phoneme),
                    viseme=phoneme_to_vrm(str(phoneme)),
                    start_s=float(start),
                    end_s=float(end),
                ),
            )

    async def push_frame(
        self,
        frame: Frame,
        direction: FrameDirection = FrameDirection.DOWNSTREAM,
    ) -> None:
        if isinstance(frame, VRMVisemeFrame):
            if self._initial_word_timestamp == -1:
                self._pending_viseme_frames.append(frame)
                return

            relative_pts = seconds_to_nanoseconds(frame.start_s)
            frame.pts = max(
                self._initial_word_timestamp,
                self._initial_word_timestamp + relative_pts - self.VISEME_LEAD_NS,
            )
            frame.transport_destination = self._transport_destination

        await super().push_frame(frame, direction)

    async def start_word_timestamps(self) -> None:
        await super().start_word_timestamps()

        pending = self._pending_viseme_frames
        self._pending_viseme_frames = []

        for frame in pending:
            await self.push_frame(frame)

    async def reset_word_timestamps(self) -> None:
        self._pending_viseme_frames.clear()
        await super().reset_word_timestamps()

    async def _process_messages(self) -> None:

        async for message in self._get_websocket():
            msg = json.loads(message)
            context_id = msg.get('context_id') if msg else None
            if not context_id or not self.audio_context_available(context_id):
                continue

            msg_type = msg.get('type')

            if msg_type == 'done':
                await self.stop_ttfb_metrics()
                await self.append_to_audio_context(
                    context_id,
                    TTSStoppedFrame(context_id=context_id),
                )
                await self.remove_audio_context(context_id)

            elif msg_type == 'timestamps':
                word_timestamps = msg['word_timestamps']
                processed_timestamps = self._normalize_word_timestamps(
                    word_timestamps['words'],
                    word_timestamps['start'],
                )
                await self.add_word_timestamps(
                    processed_timestamps,
                    context_id,
                    includes_inter_frame_spaces=(
                        True if self._word_timestamps_include_inter_frame_spaces() else None
                    ),
                )

            elif msg_type == 'phoneme_timestamps':
                await self._append_phoneme_timestamps(
                    context_id,
                    msg['phoneme_timestamps'],
                )

            elif msg_type == 'chunk':
                frame = TTSAudioRawFrame(
                    audio=base64.b64decode(msg['data']),
                    sample_rate=self.sample_rate,
                    num_channels=1,
                    context_id=context_id,
                )
                await self.append_to_audio_context(context_id, frame)

            elif msg_type == 'error':
                await self.push_frame(TTSStoppedFrame(context_id=context_id))
                await self.stop_all_metrics()
                await self.push_error(error_msg=f'Error: {msg}')
                self.reset_active_audio_context()

            elif msg_type == 'flush_done':
                pass

            else:
                await self.push_error(error_msg=f'Error, unknown message type: {msg}')
