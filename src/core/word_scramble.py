"""Word scramble game logic."""

import random
import time

from src.core.word_lists import load_words


class WordScrambleGame:
    """A word scramble game where the player unscrambles jumbled letters.

    Attributes:
        word: The original word.
        scrambled: The scrambled version.
        guesses: Number of guesses made.
        game_over: Whether the game is finished.
        won: Whether the player won.
    """

    def __init__(self, language: str = "english") -> None:
        words = load_words(language)
        self.word = random.choice(words) if words else "python"
        self.scrambled = self._scramble(self.word)
        self.guesses = 0
        self.game_over = False
        self.won = False
        self.start_time = time.time()
        self.score = 0
        self.hints_used = 0

    @staticmethod
    def _scramble(word: str) -> str:
        """Scramble a word's letters."""
        letters = list(word)
        attempts = 0
        while attempts < 20:
            random.shuffle(letters)
            scrambled = "".join(letters)
            if scrambled != word:
                return scrambled
            attempts += 1
        return scrambled

    def check(self, guess: str) -> bool:
        """Check if the guess matches the original word.

        Args:
            guess: The player's guess.

        Returns:
            True if correct.
        """
        self.guesses += 1
        if guess.strip().lower() == self.word.lower():
            self.game_over = True
            self.won = True
            elapsed = time.time() - self.start_time
            self.score = max(0, int(1000 - self.guesses * 100 - self.hints_used * 200 - int(elapsed)))
            return True
        if self.guesses >= 10:
            self.game_over = True
            self.won = False
        return False

    def get_hint(self) -> str:
        """Reveal one more letter of the word."""
        revealed = list(self.scrambled)
        unrevealed = [i for i, c in enumerate(revealed) if c != "_"]
        if not unrevealed:
            return self.word
        idx = random.choice(unrevealed)
        revealed[idx] = self.word[idx]
        self.scrambled = "".join(revealed)
        self.hints_used += 1
        return self.scrambled

    def get_display(self) -> str:
        """Get the scrambled word for display."""
        return " ".join(self.scrambled.upper())
