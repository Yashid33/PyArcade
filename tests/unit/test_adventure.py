"""Unit tests for adventure game."""

from pathlib import Path

import pytest

from src.core.adventure import AdventureGame

_STORY = Path(__file__).parent.parent.parent / "data" / "adventure" / "story.json"


class TestAdventureGame:
    def test_start(self) -> None:
        game = AdventureGame(_STORY)
        node = game.start()
        assert node.id == "start"

    def test_make_choice(self) -> None:
        game = AdventureGame(_STORY)
        game.start()
        choices = game.get_available_choices()
        assert len(choices) > 0
        next_node = game.make_choice(0)
        assert next_node is not None

    def test_inventory(self) -> None:
        game = AdventureGame(_STORY)
        game.start()
        game.make_choice(2)
        assert len(game.inventory) > 0

    def test_is_at_ending(self) -> None:
        game = AdventureGame(_STORY)
        game.start()
        assert game.is_at_ending() is False
