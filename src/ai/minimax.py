"""Minimax AI for Tic-Tac-Toe with alpha-beta pruning."""

import random


class MinimaxAI:
    """AI opponent using minimax algorithm for Tic-Tac-Toe.

    Attributes:
        depth: Maximum search depth.
        ai_player: AI's marker ('X' or 'O').
    """

    def __init__(self, difficulty: str = "hard", ai_player: str = "O") -> None:
        """Initialize the AI.

        Args:
            difficulty: 'easy' (random), 'medium' (depth-limited), 'hard' (full).
            ai_player: AI's marker.
        """
        self.ai_player = ai_player
        self.human_player = "X" if ai_player == "O" else "O"
        if difficulty == "easy":
            self._max_depth = 1
        elif difficulty == "medium":
            self._max_depth = 4
        else:
            self._max_depth = 9

    def get_best_move(self, board: list[str]) -> int:
        """Find the best move for the AI.

        Args:
            board: Current board state (9 cells).

        Returns:
            Board index of the best move.
        """
        if self._max_depth <= 1:
            return self._random_move(board)
        best_score = float("-inf")
        best_move = -1
        for i in range(9):
            if board[i] == "":
                board[i] = self.ai_player
                score = self._minimax(board, 0, False, float("-inf"), float("inf"))
                board[i] = ""
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move if best_move != -1 else self._random_move(board)

    def _random_move(self, board: list[str]) -> int:
        available = [i for i in range(9) if board[i] == ""]
        return random.choice(available) if available else -1

    def _minimax(self, board: list[str], depth: int, is_maximizing: bool, alpha: float, beta: float) -> int:
        winner = self._check_winner(board)
        if winner == self.ai_player:
            return 10 - depth
        if winner == self.human_player:
            return depth - 10
        if "" not in board or depth >= self._max_depth:
            return 0

        if is_maximizing:
            max_eval = float("-inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = self.ai_player
                    eval_score = self._minimax(board, depth + 1, False, alpha, beta)
                    board[i] = ""
                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = self.human_player
                    eval_score = self._minimax(board, depth + 1, True, alpha, beta)
                    board[i] = ""
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            return min_eval

    @staticmethod
    def _check_winner(board: list[str]) -> str | None:
        lines = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6],
        ]
        for line in lines:
            a, b, c = line
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None
