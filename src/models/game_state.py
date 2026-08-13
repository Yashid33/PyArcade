"""Game state base model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GameState:
    """Base state for any game mode.

    Attributes:
        mode: Game mode name.
        score: Current score.
        started_at: When the game started.
        finished: Whether the game is over.
    """

    mode: str
    score: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    finished: bool = False

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "score": self.score,
            "started_at": self.started_at.isoformat(),
            "finished": self.finished,
        }
