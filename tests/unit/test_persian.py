"""Unit tests for Persian language support."""

import pytest

from src.core.word_lists import load_words, get_available_languages


class TestPersianLanguage:
    def test_persian_in_languages(self) -> None:
        langs = get_available_languages()
        assert "persian" in langs

    def test_load_persian_words(self) -> None:
        words = load_words("persian")
        assert len(words) > 20
        assert all(isinstance(w, str) for w in words)

    def test_persian_words_are_lowercase(self) -> None:
        words = load_words("persian")
        for w in words:
            assert w == w.lower()
