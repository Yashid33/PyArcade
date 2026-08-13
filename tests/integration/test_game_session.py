"""Integration tests for full game sessions."""

import pytest

from src.core.hangman import HangmanGame
from src.core.tictactoe import TicTacToeGame


class TestGameSession:
    def test_hangman_full_game(self) -> None:
        game = HangmanGame(language="english")
        word = game.word
        for letter in set(word):
            game.guess(letter)
        assert game.is_won() is True

    def test_tictactoe_full_game(self) -> None:
        game = TicTacToeGame(difficulty="medium")
        moves = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        for m in moves:
            if game.game_over:
                break
            game.make_move(m)
            if not game.game_over:
                game.ai_move()
        assert game.game_over is True or "" not in game.board
