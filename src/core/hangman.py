"""Hangman game logic."""

import random
import time

from src.core.word_lists import load_words


class HangmanGame:
    """Manages a single Hangman game session.

    Attributes:
        language: Word list language.
        max_wrong: Maximum wrong guesses allowed.
        word: The secret word.
        guessed: Set of guessed letters.
        wrong_guesses: Number of wrong guesses.
        game_over: Whether the game is finished.
        won: Whether the player won.
    """

    def __init__(self, language: str = "english", max_wrong: int = 6) -> None:
        """Initialize a new Hangman game.

        Args:
            language: Word list language.
            max_wrong: Maximum wrong guesses.
        """
        self.language = language
        self.max_wrong = max_wrong
        words = load_words(language)
        self.word = random.choice(words) if words else "python"
        self.guessed: set[str] = set()
        self.wrong_guesses: int = 0
        self.game_over: bool = False
        self.won: bool = False
        self.start_time: float = time.time()
        self.score: int = 0

    def guess(self, letter: str) -> bool:
        """Guess a letter.

        Args:
            letter: Single letter to guess.

        Returns:
            True if the letter is in the word.
        """
        letter = letter.lower().strip()
        if not letter or len(letter) != 1 or not letter.isalpha():
            return False
        if letter in self.guessed:
            return False
        self.guessed.add(letter)
        if letter in self.word:
            self._check_win()
            return True
        self.wrong_guesses += 1
        self._check_lose()
        return False

    def get_display_word(self) -> str:
        """Get the word with unguessed letters hidden."""
        return " ".join(
            letter if letter in self.guessed else "_"
            for letter in self.word
        )

    def is_game_over(self) -> bool:
        return self.game_over

    def is_won(self) -> bool:
        return self.won

    def get_hint(self) -> str:
        """Get a hint by revealing an unguessed letter."""
        unguessed = [l for l in self.word if l not in self.guessed]
        if not unguessed:
            return ""
        hint_letter = random.choice(unguessed)
        self.guessed.add(hint_letter)
        self.wrong_guesses += 1
        self._check_lose()
        return hint_letter

    def get_remaining_guesses(self) -> int:
        return self.max_wrong - self.wrong_guesses

    def _check_win(self) -> None:
        if all(l in self.guessed for l in self.word):
            self.game_over = True
            self.won = True
            elapsed = time.time() - self.start_time
            self.score = max(0, int(1000 - self.wrong_guesses * 50 - int(elapsed)))

    def _check_lose(self) -> None:
        if self.wrong_guesses >= self.max_wrong:
            self.game_over = True
            self.won = False
