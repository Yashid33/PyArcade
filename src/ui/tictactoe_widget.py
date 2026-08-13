"""Tic-Tac-Toe game UI widget."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QHideEvent, QShowEvent
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.tictactoe import TicTacToeGame
from src.utils.sound_manager import SoundManager
from src.utils.stats_tracker import StatsTracker


class TicTacToeWidget(QWidget):
    """Widget for playing Tic-Tac-Toe against AI."""

    back_to_menu = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        stats_tracker: StatsTracker | None = None,
    ) -> None:
        """Initialize the Tic-Tac-Toe widget.

        Args:
            parent: Optional parent widget.
            stats_tracker: Optional statistics tracker for recording results.
        """
        super().__init__(parent)

        self._game: TicTacToeGame | None = None
        self._buttons: list[QPushButton] = []
        self._stats_tracker = stats_tracker
        self._stats_recorded = False
        self._sound = SoundManager.instance()
        self._start_new_session_on_show = True

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the widget layout and connect signals."""
        layout = QVBoxLayout(self)

        title = QLabel("Tic-Tac-Toe vs AI")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #89b4fa;"
        )
        layout.addWidget(title)

        settings_row = QHBoxLayout()

        self._diff_combo = QComboBox()
        self._diff_combo.addItems(["easy", "medium", "hard"])
        self._diff_combo.currentTextChanged.connect(self._on_difficulty_changed)

        settings_row.addWidget(QLabel("Difficulty:"))
        settings_row.addWidget(self._diff_combo)

        self._new_button = QPushButton("New Game")
        self._new_button.clicked.connect(self._on_new_game_clicked)
        settings_row.addWidget(self._new_button)

        layout.addLayout(settings_row)

        self._status_label = QLabel("Your turn (X)")
        self._status_label.setStyleSheet("font-size: 16px; color: #cdd6f4;")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        board_layout = QVBoxLayout()

        for row in range(3):
            row_layout = QHBoxLayout()

            for col in range(3):
                idx = row * 3 + col
                btn = QPushButton("")
                btn.setFixedSize(100, 100)
                btn.setStyleSheet("font-size: 24px; font-weight: bold;")
                btn.clicked.connect(lambda _, i=idx: self._on_cell_clicked(i))

                self._buttons.append(btn)
                row_layout.addWidget(btn)

            board_layout.addLayout(row_layout)

        layout.addLayout(board_layout)

        self._back_button = QPushButton("Back to Menu")
        self._back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(self._back_button)

    def showEvent(self, event: QShowEvent) -> None:
        """Start a new session automatically when the widget is opened."""
        super().showEvent(event)

        if self._start_new_session_on_show:
            self._start_new_session_on_show = False
            self._new_game()
        elif self._game is None or self._game.game_over:
            self._new_game()

    def hideEvent(self, event: QHideEvent) -> None:
        """Prepare to start a fresh session the next time the widget opens."""
        super().hideEvent(event)
        self._start_new_session_on_show = True

    def _on_new_game_clicked(self) -> None:
        """Handle user-requested new game."""
        self._sound.play_click()
        self._new_game()

    def _on_difficulty_changed(self, difficulty: str) -> None:
        """Restart the game when difficulty changes."""
        if self._game is not None:
            self._sound.play_click()
            self._new_game()

    def _on_back_clicked(self) -> None:
        """Return to the main menu."""
        self._sound.play_click()
        self.back_to_menu.emit()

    def _new_game(self) -> None:
        """Create and display a new Tic-Tac-Toe game session."""
        difficulty = self._diff_combo.currentText()
        self._game = TicTacToeGame(difficulty=difficulty)
        self._stats_recorded = False

        for btn in self._buttons:
            btn.setText("")
            btn.setEnabled(True)

        self._status_label.setText("Your turn (X)")

    def _on_cell_clicked(self, idx: int) -> None:
        """Handle a human move."""
        if not self._game or self._game.game_over:
            return

        if self._game.current_player != self._game.human_player:
            return

        board = self._game.get_board()
        if board[idx] != "":
            return

        self._sound.play_move()
        self._game.make_move(idx)
        self._update_display()

        if not self._game.game_over and self._game.current_player == self._game.ai_player:
            self._sound.play_move()
            self._game.ai_move()
            self._update_display()

    def _update_display(self) -> None:
        """Refresh the UI from the current game state."""
        if not self._game:
            return

        board = self._game.get_board()

        for i, value in enumerate(board):
            self._buttons[i].setText(value)
            self._buttons[i].setEnabled(value == "" and not self._game.game_over)

        if self._game.game_over:
            if self._game.winner:
                if self._game.winner == self._game.human_player:
                    self._status_label.setText(
                        f"You win! Score: {self._game.score}"
                    )
                else:
                    self._status_label.setText("AI wins!")
            elif self._game.is_draw:
                self._status_label.setText(f"Draw! Score: {self._game.score}")
            else:
                self._status_label.setText("Game over!")

            if not self._stats_recorded:
                self._stats_recorded = True

                if self._game.winner == self._game.human_player:
                    self._sound.play_win()
                    if self._stats_tracker is not None:
                        self._stats_tracker.record_win(
                            "tictactoe",
                            self._game.score,
                        )
                else:
                    self._sound.play_lose()
                    if self._stats_tracker is not None:
                        self._stats_tracker.record_loss("tictactoe")
        else:
            if self._game.current_player == self._game.human_player:
                self._status_label.setText("Your turn")
            else:
                self._status_label.setText("AI is thinking...")