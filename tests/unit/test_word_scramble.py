"""Unit tests for word scramble game."""

import pytest

from src.core.word_scramble import WordScrambleGame


class TestWordScrambleGame:
    def test_correct_guess(self) -> None:
        game = WordScrambleGame(language="english")
        result = game.check(game.word)
        assert result is True
        assert game.won is True

    def test_wrong_guess(self) -> None:
        game = WordScrambleGame(language="english")
        result = game.check("zzzzz")
        assert result is False
        assert game.won is False

    def test_scrambled_is_different(self) -> None:
        game = WordScrambleGame(language="english")
        if len(game.word) > 3:
            assert game.scrambled != game.word

    def test_hint(self) -> None:
        game = WordScrambleGame(language="english")
        original = game.scrambled
        game.get_hint()
        assert game.scrambled != original or len(game.word) <= 3

    def test_game_over_after_10_guesses(self) -> None:
        game = WordScrambleGame(language="english")
        for _ in range(10):
            game.check("wrong")
        assert game.game_over is True
