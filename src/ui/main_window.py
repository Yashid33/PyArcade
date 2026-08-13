"""Main application window for WordHunt."""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from src.ui.adventure_widget import AdventureWidget
from src.ui.hangman_widget import HangmanWidget
from src.ui.main_menu import MainMenuWidget
from src.ui.number_game_widget import NumberGameWidget
from src.ui.styles import MAIN_STYLE
from src.ui.tictactoe_widget import TicTacToeWidget
from src.ui.word_scramble_widget import WordScrambleWidget


class MainWindow(QMainWindow):
    """Main window with stacked widget for game navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WordHunt — Text Games")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(MAIN_STYLE)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._menu = MainMenuWidget()
        self._hangman = HangmanWidget()
        self._tictactoe = TicTacToeWidget()
        self._adventure = AdventureWidget()
        self._number_game = NumberGameWidget()
        self._word_scramble = WordScrambleWidget()

        self._stack.addWidget(self._menu)
        self._stack.addWidget(self._hangman)
        self._stack.addWidget(self._tictactoe)
        self._stack.addWidget(self._adventure)
        self._stack.addWidget(self._number_game)
        self._stack.addWidget(self._word_scramble)

        self._menu.hangman_selected.connect(lambda: self._stack.setCurrentWidget(self._hangman))
        self._menu.tictactoe_selected.connect(lambda: self._stack.setCurrentWidget(self._tictactoe))
        self._menu.adventure_selected.connect(lambda: self._stack.setCurrentWidget(self._adventure))
        self._menu.number_game_selected.connect(lambda: self._stack.setCurrentWidget(self._number_game))
        self._menu.word_scramble_selected.connect(lambda: self._stack.setCurrentWidget(self._word_scramble))

        self._hangman.back_to_menu.connect(lambda: self._stack.setCurrentWidget(self._menu))
        self._tictactoe.back_to_menu.connect(lambda: self._stack.setCurrentWidget(self._menu))
        self._adventure.back_to_menu.connect(lambda: self._stack.setCurrentWidget(self._menu))
        self._number_game.back_to_menu.connect(lambda: self._stack.setCurrentWidget(self._menu))
        self._word_scramble.back_to_menu.connect(lambda: self._stack.setCurrentWidget(self._menu))
