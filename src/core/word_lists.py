"""Multi-language word database for Hangman."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_WORD_DIR = Path(__file__).parent.parent.parent / "data" / "words"


def load_words(language: str = "english") -> list[str]:
    """Load word list for a given language.

    Args:
        language: Language name ('english', 'spanish', 'french').

    Returns:
        List of lowercase words.
    """
    path = _WORD_DIR / f"{language.lower()}.txt"
    if not path.exists():
        logger.warning("Word list not found: %s", path)
        return ["python", "hello", "world"]
    words = path.read_text(encoding="utf-8").strip().split("\n")
    return [w.strip().lower() for w in words if w.strip()]


def get_available_languages() -> list[str]:
    """Return list of available languages."""
    return ["english", "spanish", "french", "persian"]
