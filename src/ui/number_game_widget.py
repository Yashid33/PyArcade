"""Number guessing game UI widget."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QHideEvent, QShowEvent
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.number_game import NumberGame
from src.utils.sound_manager import SoundManager
from src.utils.stats_tracker import StatsTracker


class NumberGameWidget(QWidget):
    """Widget for playing the number guessing game."""

    back_to_menu = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        stats_tracker: StatsTracker | None = None,
    ) -> None:
        """Initialize the Number Guessing widget.

        Args:
            parent: Optional parent widget.
            stats_tracker: Optional statistics tracker for recording results.
        """
        super().__init__(parent)

        self._game: NumberGame | None = None
        self._stats_tracker = stats_tracker
        self._stats_recorded = False
        self._sound = SoundManager.instance()
        self._start_new_session_on_show = True

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the widget layout and connect signals."""
        layout = QVBoxLayout(self)

        title = QLabel("Number Guessing Game")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #89b4fa;"
        )
        layout.addWidget(title)

        self._hint_label = QLabel(
            "I'm thinking of a number between 1 and 100"
        )
        self._hint_label.setStyleSheet("font-size: 14px; color: #a6adc8;")
        self._hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._hint_label)

        self._result_label = QLabel("?")
        self._result_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #f9e2af;"
        )
        self._result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._result_label)

        self._status_label = QLabel("Guesses: 0/10")
        self._status_label.setStyleSheet("font-size: 14px; color: #cdd6f4;")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        input_row = QHBoxLayout()

        self._guess_input = QLineEdit()
        self._guess_input.setPlaceholderText("Enter a number...")
        self._guess_input.setMaxLength(3)
        self._guess_input.returnPressed.connect(self._on_guess)
        input_row.addWidget(self._guess_input, 1)

        self._guess_button = QPushButton("Guess")
        self._guess_button.clicked.connect(self._on_guess)
        input_row.addWidget(self._guess_button)

        layout.addLayout(input_row)

        self._new_button = QPushButton("New Game")
        self._new_button.clicked.connect(self._on_new_game_clicked)
        layout.addWidget(self._new_button)

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

    def _on_back_clicked(self) -> None:
        """Return to the main menu."""
        self._sound.play_click()
        self.back_to_menu.emit()

    def _new_game(self) -> None:
        """Create and display a new Number Guessing game session."""
        self._game = NumberGame()
        self._stats_recorded = False

        self._result_label.setText("?")
        self._result_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #f9e2af;"
        )
        self._hint_label.setText(
            "I'm thinking of a number between 1 and 100"
        )
        self._status_label.setText("Guesses: 0/10  |  Remaining: 10")

        self._guess_input.setEnabled(True)
        self._guess_input.clear()
        self._guess_button.setEnabled(True)

        self._guess_input.setFocus()

    def _on_guess(self) -> None:
        """Handle a number guess."""
        if not self._game or self._game.game_over:
            return

        text = self._guess_input.text().strip()
        if not text or not text.isdigit():
            return

        number = int(text)

        self._sound.play_move()
        self._game.guess(number)
        self._guess_input.clear()

        self._update_display(last_guess=number)

    def _update_display(self, last_guess: int | None = None) -> None:
        """Refresh the UI from the current game state."""
        if not self._game:
            return

        self._status_label.setText(
            f"Guesses: {self._game.guesses}/{self._game.max_guesses}"
            f"  |  Remaining: {self._game.get_remaining()}"
        )

        if self._game.game_over:
            self._guess_input.setEnabled(False)
            self._guess_button.setEnabled(False)

            self._result_label.setText(str(self._game.secret))

            if self._game.won:
                self._result_label.setStyleSheet(
                    "font-size: 28px; font-weight: bold; color: #a6e3a1;"
                )
                self._hint_label.setText(
                    f"You got it! Score: {self._game.score}"
                )
            else:
                self._result_label.setStyleSheet(
                    "font-size: 28px; font-weight: bold; color: #f38ba8;"
                )
                self._hint_label.setText(
                    f"Game over! The number was {self._game.secret}"
                )

            if not self._stats_recorded:
                self._stats_recorded = True

                if self._game.won:
                    self._sound.play_win()
                    if self._stats_tracker is not None:
                        self._stats_tracker.record_win(
                            "number_game",
                            self._game.score,
                        )
                else:
                    self._sound.play_lose()
                    if self._stats_tracker is not None:
                        self._stats_tracker.record_loss("number_game")
        else:
            self._guess_input.setEnabled(True)
            self._guess_button.setEnabled(True)

            if last_guess is not None:
                self._result_label.setText(str(last_guess))
                self._result_label.setStyleSheet(
                    "font-size: 28px; font-weight: bold; color: #f9e2af;"
                )

                if self._game.last_hint == "higher":
                    self._hint_label.setText("Higher!")
                elif self._game.last_hint == "lower":
                    self._hint_label.setText("Lower!")
                else:
                    self._hint_label.setText("Keep guessing!")