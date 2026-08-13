"""Number guessing game logic."""

import random
import time


class NumberGame:
    """A number guessing game where the player finds a secret number.

    Attributes:
        low: Lower bound of the range.
        high: Upper bound of the range.
        secret: The secret number to guess.
        guesses: Number of guesses made.
        max_guesses: Maximum allowed guesses.
        game_over: Whether the game is finished.
        won: Whether the player won.
    """

    def __init__(self, low: int = 1, high: int = 100, max_guesses: int = 10) -> None:
        self.low = low
        self.high = high
        self.secret = random.randint(low, high)
        self.guesses = 0
        self.max_guesses = max_guesses
        self.game_over = False
        self.won = False
        self.start_time = time.time()
        self.score = 0
        self.last_hint = ""

    def guess(self, number: int) -> str:
        """Make a guess and return a hint.

        Args:
            number: The guessed number.

        Returns:
            Hint string: 'higher', 'lower', or 'correct'.
        """
        if self.game_over:
            return "game over"
        self.guesses += 1
        if number == self.secret:
            self.game_over = True
            self.won = True
            elapsed = time.time() - self.start_time
            self.score = max(0, int(1000 - self.guesses * 50 - int(elapsed)))
            self.last_hint = "correct"
            return "correct"
        if self.guesses >= self.max_guesses:
            self.game_over = True
            self.won = False
            self.last_hint = "game over"
            return "game over"
        if number < self.secret:
            self.last_hint = "higher"
            return "higher"
        self.last_hint = "lower"
        return "lower"

    def get_range_display(self) -> str:
        """Get the current valid range hint."""
        return f"Range: {self.low} - {self.high}"

    def get_remaining(self) -> int:
        return self.max_guesses - self.guesses
