"""
Unit tests for api.v1.bot.viseme_processor – guess_viseme() and CHAR_TO_VRM.
"""
from __future__ import annotations

from api.v1.bot.viseme_processor import CHAR_TO_VRM, guess_viseme


class TestCharToVRM:
    def test_english_vowels(self):
        assert CHAR_TO_VRM['a'] == 'aa'
        assert CHAR_TO_VRM['o'] == 'oh'
        assert CHAR_TO_VRM['u'] == 'ou'
        assert CHAR_TO_VRM['e'] == 'ee'
        assert CHAR_TO_VRM['i'] == 'ih'

    def test_russian_vowels(self):
        assert CHAR_TO_VRM['а'] == 'aa'
        assert CHAR_TO_VRM['о'] == 'oh'
        assert CHAR_TO_VRM['у'] == 'ou'
        assert CHAR_TO_VRM['е'] == 'ee'
        assert CHAR_TO_VRM['и'] == 'ih'
        assert CHAR_TO_VRM['э'] == 'ee'
        assert CHAR_TO_VRM['ю'] == 'ou'
        assert CHAR_TO_VRM['я'] == 'aa'
        assert CHAR_TO_VRM['ё'] == 'aa'


class TestGuessViseme:
    def test_first_vowel_wins(self):
        assert guess_viseme("hello") == 'ee'

    def test_russian_word(self):
        assert guess_viseme("привет") == 'ih'

    def test_no_vowel_returns_neutral(self):
        assert guess_viseme("bcdfg") == 'neutral'

    def test_empty_string(self):
        assert guess_viseme("") == 'neutral'

    def test_case_insensitive(self):
        assert guess_viseme("Apple") == 'aa'

    def test_single_vowel(self):
        assert guess_viseme("a") == 'aa'
        assert guess_viseme("o") == 'oh'
        assert guess_viseme("u") == 'ou'

    def test_consonants_only(self):
        assert guess_viseme("bcdfg") == 'neutral'
