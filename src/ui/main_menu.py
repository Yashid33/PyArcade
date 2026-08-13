"""Main menu widget for game selection."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class MainMenuWidget(QWidget):
    """Main menu for selecting a game mode."""

    hangman_selected = pyqtSignal()
    tictactoe_selected = pyqtSignal()
    adventure_selected = pyqtSignal()
    number_game_selected = pyqtSignal()
    word_scramble_selected = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("WordHunt")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #89b4fa;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Text Games Collection")
        subtitle.setStyleSheet("font-size: 16px; color: #a6adc8;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(30)

        hangman_btn = QPushButton("Hangman")
        hangman_btn.setFixedWidth(250)
        hangman_btn.clicked.connect(self.hangman_selected.emit)
        layout.addWidget(hangman_btn, alignment=Qt.AlignCenter)

        ttt_btn = QPushButton("Tic-Tac-Toe vs AI")
        ttt_btn.setFixedWidth(250)
        ttt_btn.clicked.connect(self.tictactoe_selected.emit)
        layout.addWidget(ttt_btn, alignment=Qt.AlignCenter)

        adv_btn = QPushButton("Adventure Quest")
        adv_btn.setFixedWidth(250)
        adv_btn.clicked.connect(self.adventure_selected.emit)
        layout.addWidget(adv_btn, alignment=Qt.AlignCenter)

        num_btn = QPushButton("Number Guessing")
        num_btn.setFixedWidth(250)
        num_btn.clicked.connect(self.number_game_selected.emit)
        layout.addWidget(num_btn, alignment=Qt.AlignCenter)

        scramble_btn = QPushButton("Word Scramble")
        scramble_btn.setFixedWidth(250)
        scramble_btn.clicked.connect(self.word_scramble_selected.emit)
        layout.addWidget(scramble_btn, alignment=Qt.AlignCenter)
