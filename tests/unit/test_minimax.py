"""Unit tests for minimax AI."""

import pytest

from src.ai.minimax import MinimaxAI


class TestMinimaxAI:
    def test_win_if_possible(self) -> None:
        ai = MinimaxAI(difficulty="hard", ai_player="O")
        board = ["O", "O", "", "X", "", "", "X", "", ""]
        move = ai.get_best_move(board)
        assert move == 2

    def test_block_opponent_win(self) -> None:
        ai = MinimaxAI(difficulty="hard", ai_player="O")
        board = ["X", "X", "", "O", "", "", "", "", ""]
        move = ai.get_best_move(board)
        assert move == 2

    def test_center_first(self) -> None:
        ai = MinimaxAI(difficulty="hard", ai_player="O")
        board = [""] * 9
        move = ai.get_best_move(board)
        assert move in [0, 2, 4, 6, 8]
