"""Unit tests for Hangman game."""

import pytest

from src.core.hangman import HangmanGame


class TestHangmanGame:
    def test_correct_guess(self) -> None:
        game = HangmanGame(language="english")
        game.word = "cat"
        result = game.guess("c")
        assert result is True
        assert "c" in game.guessed

    def test_wrong_guess(self) -> None:
        game = HangmanGame(language="english")
        game.word = "cat"
        result = game.guess("z")
        assert result is False
        assert game.wrong_guesses == 1

    def test_display_word(self) -> None:
        game = HangmanGame(language="english")
        game.word = "cat"
        game.guess("c")
        assert game.get_display_word() == "c _ _"

    def test_win(self) -> None:
        game = HangmanGame(language="english")
        game.word = "ab"
        game.guess("a")
        game.guess("b")
        assert game.is_won() is True
        assert game.is_game_over() is True

    def test_lose(self) -> None:
        game = HangmanGame(language="english", max_wrong=2)
        game.word = "cat"
        game.guess("z")
        game.guess("x")
        assert game.is_won() is False
        assert game.is_game_over() is True

    def test_duplicate_guess(self) -> None:
        game = HangmanGame(language="english")
        game.word = "cat"
        game.guess("c")
        result = game.guess("c")
        assert result is False
