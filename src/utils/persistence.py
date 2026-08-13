"""Game state persistence utilities."""

import json
import logging
from pathlib import Path

from src.models.player_stats import PlayerStats

logger = logging.getLogger(__name__)


def load_stats(path: Path) -> PlayerStats:
    """Load player statistics from disk."""
    if not path.exists():
        return PlayerStats()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return PlayerStats.from_dict(data)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to load stats: %s", e)
        return PlayerStats()


def save_stats(stats: PlayerStats, path: Path) -> None:
    """Save player statistics to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats.to_dict(), f, indent=2)
