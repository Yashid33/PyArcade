"""Unit tests for number guessing game."""

import pytest

from src.core.number_game import NumberGame


class TestNumberGame:
    def test_correct_guess(self) -> None:
        game = NumberGame(low=1, high=10)
        game.secret = 5
        result = game.guess(5)
        assert result == "correct"
        assert game.won is True

    def test_higher_hint(self) -> None:
        game = NumberGame(low=1, high=100)
        game.secret = 50
        result = game.guess(30)
        assert result == "higher"

    def test_lower_hint(self) -> None:
        game = NumberGame(low=1, high=100)
        game.secret = 50
        result = game.guess(80)
        assert result == "lower"

    def test_game_over(self) -> None:
        game = NumberGame(low=1, high=10, max_guesses=3)
        game.secret = 100
        game.guess(1)
        game.guess(2)
        game.guess(3)
        assert game.game_over is True
        assert game.won is False

    def test_score(self) -> None:
        game = NumberGame(low=1, high=10)
        game.secret = 5
        game.guess(5)
        assert game.score > 0
