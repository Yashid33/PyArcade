"""Hangman game UI widget."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QHideEvent, QShowEvent
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.hangman import HangmanGame
from src.utils.sound_manager import SoundManager
from src.utils.stats_tracker import StatsTracker


class HangmanWidget(QWidget):
    """Widget for playing Hangman."""

    back_to_menu = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        stats_tracker: StatsTracker | None = None,
    ) -> None:
        """Initialize the Hangman widget.

        Args:
            parent: Optional parent widget.
            stats_tracker: Optional statistics tracker for recording results.
        """
        super().__init__(parent)

        self._game: HangmanGame | None = None
        self._stats_tracker = stats_tracker
        self._stats_recorded = False
        self._sound = SoundManager.instance()
        self._start_new_session_on_show = True

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the widget layout and connect signals."""
        layout = QVBoxLayout(self)

        self._title_label = QLabel("Hangman")
        self._title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #89b4fa;"
        )
        layout.addWidget(self._title_label)

        settings_row = QHBoxLayout()

        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["english", "spanish", "french", "persian"])
        self._lang_combo.currentTextChanged.connect(self._on_language_changed)

        settings_row.addWidget(QLabel("Language:"))
        settings_row.addWidget(self._lang_combo)

        self._new_button = QPushButton("New Game")
        self._new_button.clicked.connect(self._on_new_game_clicked)
        settings_row.addWidget(self._new_button)

        layout.addLayout(settings_row)

        self._word_label = QLabel("")
        self._word_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #a6e3a1; letter-spacing: 4px;"
        )
        self._word_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._word_label)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("font-size: 16px; color: #cdd6f4;")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        input_row = QHBoxLayout()

        self._guess_input = QLineEdit()
        self._guess_input.setPlaceholderText("Enter a letter...")
        self._guess_input.setMaxLength(1)
        self._guess_input.returnPressed.connect(self._on_guess)
        input_row.addWidget(self._guess_input, 1)

        self._guess_button = QPushButton("Guess")
        self._guess_button.clicked.connect(self._on_guess)
        input_row.addWidget(self._guess_button)

        self._hint_button = QPushButton("Hint")
        self._hint_button.clicked.connect(self._on_hint)
        input_row.addWidget(self._hint_button)

        layout.addLayout(input_row)

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

    def _on_language_changed(self, language: str) -> None:
        """Restart the game when the selected language changes."""
        if self._game is not None:
            self._sound.play_click()
            self._new_game()

    def _on_back_clicked(self) -> None:
        """Return to the main menu."""
        self._sound.play_click()
        self.back_to_menu.emit()

    def _new_game(self) -> None:
        """Create and display a new Hangman game session."""
        language = self._lang_combo.currentText()
        self._game = HangmanGame(language=language)
        self._stats_recorded = False

        self._guess_input.setEnabled(True)
        self._guess_input.clear()
        self._guess_button.setEnabled(True)
        self._hint_button.setEnabled(True)
        self._new_button.setEnabled(True)

        self._update_display()
        self._guess_input.setFocus()

    def _on_guess(self) -> None:
        """Handle a letter guess."""
        if not self._game or self._game.game_over:
            return

        letter = self._guess_input.text().strip()
        if not letter:
            return

        self._sound.play_move()
        self._game.guess(letter)
        self._guess_input.clear()
        self._update_display()

    def _on_hint(self) -> None:
        """Handle a hint request."""
        if not self._game or self._game.game_over:
            return

        self._sound.play_click()
        self._game.get_hint()
        self._update_display()

    def _update_display(self) -> None:
        """Refresh the UI from the current game state."""
        if not self._game:
            return

        self._word_label.setText(self._game.get_display_word())

        remaining = self._game.get_remaining_guesses()
        status_text = (
            f"Wrong guesses: {self._game.wrong_guesses}/{self._game.max_wrong}"
            f"  |  Remaining: {remaining}"
        )
        self._status_label.setText(status_text)

        if self._game.is_game_over():
            self._guess_input.setEnabled(False)
            self._guess_button.setEnabled(False)
            self._hint_button.setEnabled(False)

            if self._game.won:
                self._status_label.setText(
                    f"You won! Score: {self._game.score}  |  Word: {self._game.word}"
                )
            else:
                self._status_label.setText(
                    f"Game over! The word was: {self._game.word}"
                )

            if not self._stats_recorded:
                self._stats_recorded = True

                if self._game.won:
                    self._sound.play_win()
                    if self._stats_tracker is not None:
                        self._stats_tracker.record_win("hangman", self._game.score)
                else:
                    self._sound.play_lose()
                    if self._stats_tracker is not None:
                        self._stats_tracker.record_loss("hangman")