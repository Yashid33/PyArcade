"""Unit tests for Tic-Tac-Toe game."""

import pytest

from src.core.tictactoe import TicTacToeGame


class TestTicTacToeGame:
    def test_make_move(self) -> None:
        game = TicTacToeGame(difficulty="easy")
        assert game.make_move(4) is True
        assert game.board[4] == "X"

    def test_invalid_move(self) -> None:
        game = TicTacToeGame(difficulty="easy")
        game.make_move(4)
        assert game.make_move(4) is False

    def test_ai_move(self) -> None:
        game = TicTacToeGame(difficulty="hard", human_player="X")
        game.make_move(0)
        pos = game.ai_move()
        assert pos >= 0
        assert game.board[pos] == "O"

    def test_win_detection(self) -> None:
        game = TicTacToeGame(difficulty="easy")
        game.board = ["X", "X", "X", "", "", "", "", "", ""]
        game._check_game_state()
        assert game.winner == "X"

    def test_draw(self) -> None:
        game = TicTacToeGame(difficulty="easy")
        game.board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        game._check_game_state()
        assert game.is_draw is True
