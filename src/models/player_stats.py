"""Player statistics model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlayerStats:
    """Tracks player performance across games.

    Attributes:
        total_games: Number of games played.
        wins: Number of wins.
        losses: Number of losses.
        high_scores: Best score per game mode.
        last_played: Timestamp of last game.
    """

    total_games: int = 0
    wins: int = 0
    losses: int = 0
    high_scores: dict[str, int] = field(default_factory=dict)
    last_played: datetime = field(default_factory=datetime.now)

    def record_win(self, mode: str, score: int) -> None:
        self.total_games += 1
        self.wins += 1
        if score > self.high_scores.get(mode, 0):
            self.high_scores[mode] = score
        self.last_played = datetime.now()

    def record_loss(self, mode: str) -> None:
        self.total_games += 1
        self.losses += 1
        self.last_played = datetime.now()

    @property
    def win_rate(self) -> float:
        if self.total_games == 0:
            return 0.0
        return self.wins / self.total_games

    def to_dict(self) -> dict:
        return {
            "total_games": self.total_games,
            "wins": self.wins,
            "losses": self.losses,
            "high_scores": self.high_scores,
            "last_played": self.last_played.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerStats":
        return cls(
            total_games=data.get("total_games", 0),
            wins=data.get("wins", 0),
            losses=data.get("losses", 0),
            high_scores=data.get("high_scores", {}),
            last_played=datetime.fromisoformat(data["last_played"]) if "last_played" in data else datetime.now(),
        )
