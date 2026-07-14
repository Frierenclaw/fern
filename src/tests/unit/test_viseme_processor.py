"""Tests for Cartesia phoneme timing and VRM viseme delivery."""

import json
from unittest.mock import AsyncMock

import pytest
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.cartesia.tts import CartesiaTTSService

from api.v1.bot.tts.cartesia import (
    VisemeCartesiaTTSService,
    VRMVisemeFrame,
    phoneme_to_vrm,
)
from api.v1.bot.tts.viseme_processor import (
    CHAR_TO_VRM,
    VRMVisemeProcessor,
    guess_viseme,
)


class TestCharToVRM:
    def test_english_vowels(self):
        assert CHAR_TO_VRM["a"] == "aa"
        assert CHAR_TO_VRM["o"] == "oh"
        assert CHAR_TO_VRM["u"] == "ou"
        assert CHAR_TO_VRM["e"] == "ee"
        assert CHAR_TO_VRM["i"] == "ih"

    def test_russian_vowels(self):
        assert CHAR_TO_VRM["а"] == "aa"
        assert CHAR_TO_VRM["о"] == "oh"
        assert CHAR_TO_VRM["у"] == "ou"
        assert CHAR_TO_VRM["е"] == "ee"
        assert CHAR_TO_VRM["и"] == "ih"
        assert CHAR_TO_VRM["э"] == "ee"
        assert CHAR_TO_VRM["ю"] == "ou"
        assert CHAR_TO_VRM["я"] == "aa"
        assert CHAR_TO_VRM["ё"] == "aa"


class TestGuessViseme:
    @pytest.mark.parametrize(
        ("word", "expected"),
        [
            ("hello", "ee"),
            ("привет", "ih"),
            ("bcdfg", "neutral"),
            ("", "neutral"),
            ("Apple", "aa"),
            ("a", "aa"),
            ("o", "oh"),
            ("u", "ou"),
        ],
    )
    def test_word_mapping(self, word: str, expected: str):
        assert guess_viseme(word) == expected


class TestPhonemeToVRM:
    @pytest.mark.parametrize(
        ("phoneme", "expected"),
        [
            ("a", "aa"),
            ("ɐ", "aa"),
            ("ˈi", "ih"),
            ("ɨ", "ih"),
            ("uː", "ou"),
            ("ɛ", "ee"),
            ("ə", "ee"),
            ("ɔ", "oh"),
            ("m", "neutral"),
            ("t͡ɕ", "neutral"),
        ],
    )
    def test_ipa_mapping(self, phoneme: str, expected: str):
        assert phoneme_to_vrm(phoneme) == expected


class TestVisemeCartesiaTTSService:
    def make_service(self) -> VisemeCartesiaTTSService:
        return VisemeCartesiaTTSService(
            api_key="test-key",
            settings=VisemeCartesiaTTSService.Settings(
                voice="test-voice",
                model="sonic-3.5",
            ),
        )

    def test_enables_phoneme_timestamps(self):
        service = self.make_service()

        message = service._build_msg(text="Привет", context_id="ctx")

        assert '"add_phoneme_timestamps": true' in message
        assert '"add_timestamps": true' in message

    async def test_converts_cartesia_timestamps_to_frames(self):
        service = self.make_service()
        service.append_to_audio_context = AsyncMock()

        await service._append_phoneme_timestamps(
            "ctx",
            {
                "phonemes": ["p", "ɐ", "r"],
                "start": [0.0, 0.08, 0.18],
                "end": [0.08, 0.18, 0.24],
            },
        )

        assert service.append_to_audio_context.await_count == 3
        frames = [call.args[1] for call in service.append_to_audio_context.await_args_list]
        assert all(isinstance(frame, VRMVisemeFrame) for frame in frames)
        assert [frame.viseme for frame in frames] == ["neutral", "aa", "neutral"]
        assert frames[1].start_s == 0.08
        assert frames[1].end_s == 0.18

    async def test_schedules_viseme_against_audio_pts(self, monkeypatch):
        base_push = AsyncMock()
        monkeypatch.setattr(CartesiaTTSService, "push_frame", base_push)
        service = self.make_service()
        service._initial_word_timestamp = 1_000_000_000
        service._transport_destination = "livekit"
        frame = VRMVisemeFrame(
            context_id="ctx",
            phoneme="a",
            viseme="aa",
            start_s=0.08,
            end_s=0.18,
        )

        await service.push_frame(frame)

        assert frame.pts == 1_050_000_000
        assert frame.transport_destination == "livekit"
        base_push.assert_awaited_once_with(frame, FrameDirection.DOWNSTREAM)


class TestVRMVisemeProcessor:
    async def test_publishes_timed_viseme_with_public_transport_api(self):
        transport = AsyncMock()
        processor = VRMVisemeProcessor(transport)
        processor.push_frame = AsyncMock()
        frame = VRMVisemeFrame(
            context_id="ctx",
            phoneme="a",
            viseme="aa",
            start_s=0.08,
            end_s=0.18,
        )
        frame.pts = 1_050_000_000

        await processor.process_frame(frame, FrameDirection.DOWNSTREAM)

        transport.send_message.assert_awaited_once()
        payload = json.loads(transport.send_message.await_args.args[0])
        assert payload == {
            "type": "vrm_viseme",
            "context_id": "ctx",
            "phoneme": "a",
            "viseme": "aa",
            "duration_ms": 100,
        }
        processor.push_frame.assert_awaited_once_with(frame, FrameDirection.DOWNSTREAM)
