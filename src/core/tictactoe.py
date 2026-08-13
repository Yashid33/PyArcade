"""Tic-Tac-Toe game logic with AI opponent."""

from src.ai.minimax import MinimaxAI


class TicTacToeGame:
    """Manages a Tic-Tac-Toe game with AI opponent.

    Attributes:
        board: 9-element list of 'X', 'O', or ''.
        current_player: Current player ('X' or 'O').
        game_over: Whether the game is finished.
        winner: Winner marker or None.
    """

    def __init__(self, difficulty: str = "hard", human_player: str = "X") -> None:
        """Initialize a new game.

        Args:
            difficulty: AI difficulty level.
            human_player: Human's marker ('X' or 'O').
        """
        self.board: list[str] = [""] * 9
        self.current_player = "X"
        self.game_over = False
        self.winner: str | None = None
        self.is_draw = False
        self.human_player = human_player
        self.ai_player = "O" if human_player == "X" else "X"
        self.ai = MinimaxAI(difficulty=difficulty, ai_player=self.ai_player)
        self.score = 0

    def make_move(self, position: int) -> bool:
        """Make a move on the board.

        Args:
            position: Board index (0-8).

        Returns:
            True if the move was valid.
        """
        if self.game_over or position < 0 or position >= 9:
            return False
        if self.board[position] != "":
            return False
        self.board[position] = self.current_player
        self._check_game_state()
        if not self.game_over:
            self.current_player = self.ai_player if self.current_player == self.human_player else self.human_player
        return True

    def ai_move(self) -> int:
        """Let the AI make a move.

        Returns:
            The position the AI moved to, or -1 if no move possible.
        """
        if self.game_over or self.current_player != self.ai_player:
            return -1
        pos = self.ai.get_best_move(self.board)
        if pos >= 0:
            self.board[pos] = self.ai_player
            self._check_game_state()
            if not self.game_over:
                self.current_player = self.human_player
        return pos

    def get_board(self) -> list[str]:
        return list(self.board)

    def get_display(self) -> str:
        """Get a formatted board string."""
        cells = []
        for i, val in enumerate(self.board):
            cells.append(val if val else str(i + 1))
        return (
            f" {cells[0]} | {cells[1]} | {cells[2]}\n"
            f"---+---+---\n"
            f" {cells[3]} | {cells[4]} | {cells[5]}\n"
            f"---+---+---\n"
            f" {cells[6]} | {cells[7]} | {cells[8]}"
        )

    def _check_game_state(self) -> None:
        lines = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6],
        ]
        for line in lines:
            a, b, c = line
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                self.game_over = True
                self.score = 100 if self.winner == self.human_player else 0
                return
        if "" not in self.board:
            self.is_draw = True
            self.game_over = True
            self.score = 50
