"""Statistics tracking for games."""

import logging
from pathlib import Path

from src.models.player_stats import PlayerStats
from src.utils.persistence import load_stats, save_stats

logger = logging.getLogger(__name__)


class StatsTracker:
    """Tracks and persists player statistics."""

    def __init__(self, data_dir: Path | None = None) -> None:
        """Initialize the tracker."""
        self._path = (data_dir or Path(__file__).parent.parent.parent / "data") / "stats.json"
        self._stats = load_stats(self._path)

    @property
    def stats(self) -> PlayerStats:
        return self._stats

    def record_win(self, mode: str, score: int) -> None:
        self._stats.record_win(mode, score)
        save_stats(self._stats, self._path)

    def record_loss(self, mode: str) -> None:
        self._stats.record_loss(mode)
        save_stats(self._stats, self._path)

    def get_high_score(self, mode: str) -> int:
        return self._stats.high_scores.get(mode, 0)
