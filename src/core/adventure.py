"""Text-based adventure game engine."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.models.adventure_node import AdventureNode, Choice

logger = logging.getLogger(__name__)


class AdventureGame:
    """Manages a branching text adventure game.

    Attributes:
        language: Active story language.
        story_name: Active story file name, if one is selected.
        nodes: Dictionary of all story nodes.
        current_id: Current node ID.
        inventory: Items the player has collected.
    """

    DEFAULT_LANGUAGES: tuple[str, ...] = ("english", "persian")

    def __init__(
        self,
        story_path: Path | None = None,
        language: str = "english",
        story_name: str | None = None,
    ) -> None:
        """Initialize the adventure game.

        Args:
            story_path: Optional path to a story JSON file.
            language: Story language used for built-in/default story lookup.
            story_name: Optional story file name inside data/adventure.
        """
        self.language: str = language.strip().lower()
        self.story_name: str | None = story_name
        self.nodes: dict[str, AdventureNode] = {}
        self.current_id: str = "start"
        self.inventory: list[str] = []
        self._steps: int = 0

        if story_path is not None:
            story_path = Path(story_path)

        if story_name:
            self._load_selected_story(self._story_path_for_name(story_name))
        elif story_path is not None:
            self._load_selected_story(story_path)
        else:
            self._load_selected_story(None)

        if not self.nodes:
            self._load_builtin_story()

        self._ensure_current_id()

    @classmethod
    def stories_directory(cls) -> Path:
        """Return the directory containing adventure story files."""
        return (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "adventure"
        )

    @classmethod
    def get_available_story_names(cls) -> list[str]:
        """Return available story names from data/adventure/*.json."""
        directory = cls.stories_directory()

        if not directory.exists():
            return []

        names: list[str] = []

        for path in sorted(directory.glob("*.json")):
            if path.is_file():
                names.append(path.stem)

        return names

    @classmethod
    def _story_path_for_name(cls, story_name: str) -> Path:
        """Convert a story name to a safe JSON file path."""
        safe_name = Path(story_name).name

        if safe_name.lower().endswith(".json"):
            safe_name = safe_name[:-5]

        return cls.stories_directory() / f"{safe_name}.json"

    def set_story(
        self,
        story_name: str,
        language: str | None = None,
    ) -> AdventureNode:
        """Load a story file by name and restart the adventure.

        Args:
            story_name: Story file name without directory path.
            language: Optional language to activate alongside the story.

        Returns:
            The starting node of the newly loaded story.
        """
        if language:
            self.language = language.strip().lower()

        self.story_name = story_name
        self.nodes.clear()

        self._load_selected_story(self._story_path_for_name(story_name))

        if not self.nodes:
            self._load_builtin_story()

        self._ensure_current_id()
        return self.start()

    def set_language(
        self,
        language: str,
        story_path: Path | None = None,
    ) -> AdventureNode:
        """Switch the active story language and restart the adventure.

        Args:
            language: New language name.
            story_path: Optional explicit story path for the new language.

        Returns:
            The starting node for the newly loaded story.
        """
        self.language = language.strip().lower()
        self.story_name = None
        self.nodes.clear()

        if story_path is not None:
            story_path = Path(story_path)

        self._load_selected_story(story_path)

        if not self.nodes:
            self._load_builtin_story()

        self._ensure_current_id()
        return self.start()

    def _default_story_path(self) -> Path:
        """Return the default story path for the current settings."""
        if self.story_name:
            return self._story_path_for_name(self.story_name)

        base_dir = self.stories_directory()

        language_path = base_dir / f"story_{self.language}.json"
        if language_path.exists():
            return language_path

        legacy_path = base_dir / "story.json"
        if self.language == "english" and legacy_path.exists():
            return legacy_path

        return language_path

    def _load_selected_story(self, story_path: Path | None = None) -> None:
        """Load a story from disk if available."""
        path = story_path or self._default_story_path()

        if path.exists():
            self._load_story(path)

        if not self.nodes and story_path is None and self.language != "english":
            fallback_path = self._default_story_path_for_language("english")

            if fallback_path.exists():
                logger.warning(
                    "Story file for '%s' not found. Falling back to English story.",
                    self.language,
                )
                self._load_story(fallback_path)

    def _default_story_path_for_language(self, language: str) -> Path:
        """Return the default story path for a specific language."""
        return (
            self.stories_directory()
            / f"story_{language.lower()}.json"
        )

    def _load_story(self, path: Path) -> None:
        """Load story nodes from JSON."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to load adventure story from %s: %s", path, exc)
            return

        if isinstance(data, dict):
            node_list = data.get("nodes", [])
        elif isinstance(data, list):
            node_list = data
        else:
            logger.error("Invalid adventure story format in %s", path)
            return

        for node_data in node_list:
            try:
                node = AdventureNode.from_dict(node_data)
                self.nodes[node.id] = node
            except Exception as exc:
                logger.error("Invalid adventure node in %s: %s", path, exc)

        logger.info("Loaded %d adventure nodes from %s", len(self.nodes), path)
        self._ensure_current_id()

    def _ensure_current_id(self) -> None:
        """Ensure current_id points to a valid node."""
        if not self.nodes:
            return

        if self.current_id not in self.nodes:
            self.current_id = next(iter(self.nodes))

    def _load_builtin_story(self) -> None:
        """Load a built-in story when no valid story file is available."""
        if self._use_persian_builtin():
            story_data = self._builtin_persian_story()
        else:
            story_data = self._builtin_english_story()

        self.nodes.clear()

        for node_data in story_data.get("nodes", []):
            node = AdventureNode.from_dict(node_data)
            self.nodes[node.id] = node

        logger.info(
            "Loaded built-in %s adventure with %d nodes",
            self.language,
            len(self.nodes),
        )

    def _use_persian_builtin(self) -> bool:
        """Return True when the active language should use Persian content."""
        return self.language in {"persian", "farsi", "fa"}

    def _builtin_english_story(self) -> dict:
        """Return a small built-in English story."""
        return {
            "nodes": [
                {
                    "id": "start",
                    "title": "The Crossroads",
                    "text": (
                        "You stand at a crossroads. A cold wind moves through the grass. "
                        "A dark forest lies to the west, and a rocky cave opens to the east."
                    ),
                    "choices": [
                        {"text": "Enter the forest", "next": "forest"},
                        {"text": "Approach the cave", "next": "cave"},
                    ],
                },
                {
                    "id": "forest",
                    "title": "Whispering Forest",
                    "text": (
                        "The trees whisper above you. Among the roots of an old oak, "
                        "you find a sturdy lantern filled with oil."
                    ),
                    "items_available": ["lantern"],
                    "choices": [
                        {"text": "Take the lantern and head to the cave", "next": "cave"},
                        {"text": "Return to the crossroads", "next": "start"},
                    ],
                },
                {
                    "id": "cave",
                    "title": "Dark Cave",
                    "text": (
                        "The mouth of the cave is dark and silent. Water drips somewhere inside. "
                        "You can barely see more than a few steps ahead."
                    ),
                    "choices": [
                        {"text": "Enter without light", "next": "lost_end"},
                        {
                            "text": "Use the lantern",
                            "next": "treasure",
                            "requires_item": "lantern",
                        },
                        {"text": "Return to the forest", "next": "forest"},
                    ],
                },
                {
                    "id": "treasure",
                    "title": "Hidden Treasure",
                    "text": (
                        "The lantern light reveals ancient carvings on the cave walls. "
                        "Behind them, you find a small chest filled with old coins. "
                        "You have completed the adventure!"
                    ),
                    "is_ending": True,
                },
                {
                    "id": "lost_end",
                    "title": "Lost in Darkness",
                    "text": (
                        "Without light, you stumble deeper into the cave. "
                        "The entrance disappears behind you, and the darkness closes in. "
                        "Your adventure ends here."
                    ),
                    "is_ending": True,
                },
            ]
        }

    def _builtin_persian_story(self) -> dict:
        """Return a small built-in Persian story."""
        return {
            "nodes": [
                {
                    "id": "start",
                    "title": "دوراهی",
                    "text": (
                        "شما بر سر دوراهی ایستاده‌اید. باد سردی میان علف‌ها می‌پیچد. "
                        "جنگلی تاریک در غرب و غاری سنگی در شرق دیده می‌شود."
                    ),
                    "choices": [
                        {"text": "وارد شدن به جنگل", "next": "forest"},
                        {"text": "نزدیک شدن به غار", "next": "cave"},
                    ],
                },
                {
                    "id": "forest",
                    "title": "جنگل زمزمه‌کننده",
                    "text": (
                        "درختان بالای سر شما زمزمه می‌کنند. میان ریشه‌های یک درخت بلوط قدیمی، "
                        "یک فانوس محکم و پر از روغن پیدا می‌کنید."
                    ),
                    "items_available": ["lantern"],
                    "choices": [
                        {"text": "فانوس را بردار و به سمت غار برو", "next": "cave"},
                        {"text": "به دوراهی بازگرد", "next": "start"},
                    ],
                },
                {
                    "id": "cave",
                    "title": "غار تاریک",
                    "text": (
                        "دهانه‌ی غار تاریک و ساکت است. صدای چکیدن آب از درون شنیده می‌شود. "
                        "به‌سختی می‌توانید چند قدم جلوتر را ببینید."
                    ),
                    "choices": [
                        {"text": "بدون نور وارد غار شو", "next": "lost_end"},
                        {
                            "text": "از فانوس استفاده کن",
                            "next": "treasure",
                            "requires_item": "lantern",
                        },
                        {"text": "به جنگل بازگرد", "next": "forest"},
                    ],
                },
                {
                    "id": "treasure",
                    "title": "گنج پنهان",
                    "text": (
                        "نور فانوس نقش‌های باستانی روی دیوارهای غار را آشکار می‌کند. "
                        "پشت آن‌ها صندوقچه‌ای پر از سکه‌های قدیمی پیدا می‌کنید. "
                        "ماجراجویی شما با موفقیت پایان یافت!"
                    ),
                    "is_ending": True,
                },
                {
                    "id": "lost_end",
                    "title": "گم‌شده در تاریکی",
                    "text": (
                        "بدون نور، در عمق غار تلپ می‌خورید و پیش می‌روید. "
                        "ورودی غار پشت سر شما گم می‌شود و تاریکی شما را فرا می‌گیرد. "
                        "ماجراجویی شما این‌گونه پایان می‌یابد."
                    ),
                    "is_ending": True,
                },
            ]
        }

    def start(self) -> AdventureNode:
        """Start the adventure from the beginning."""
        if not self.nodes:
            self._load_builtin_story()

        if "start" in self.nodes:
            self.current_id = "start"
        elif self.nodes:
            self.current_id = next(iter(self.nodes))

        self.inventory.clear()
        self._steps = 0

        return self.get_current_node()

    def get_current_node(self) -> AdventureNode:
        """Get the current story node."""
        node = self.nodes.get(self.current_id)

        if node is None:
            raise ValueError(f"Unknown node: {self.current_id}")

        return node

    def get_available_choices(self) -> list[Choice]:
        """Get choices available at the current node, filtered by inventory."""
        node = self.get_current_node()
        available: list[Choice] = []

        for choice in node.choices:
            if choice.requires_item is None or choice.requires_item in self.inventory:
                available.append(choice)

        return available

    def make_choice(self, choice_idx: int) -> AdventureNode | None:
        """Make a choice and move to the next node.

        Args:
            choice_idx: Index of the choice to make.

        Returns:
            The next node, or None if the choice is invalid.
        """
        available = self.get_available_choices()

        if choice_idx < 0 or choice_idx >= len(available):
            return None

        choice = available[choice_idx]
        next_node = self.nodes.get(choice.next)

        if next_node is None:
            return None

        self.current_id = choice.next
        self._steps += 1

        for item in next_node.items_available:
            if item not in self.inventory:
                self.inventory.append(item)

        return next_node

    def is_at_ending(self) -> bool:
        """Check if the current node is an ending."""
        return self.get_current_node().is_ending

    def get_ending_title(self) -> str:
        """Get the title of the current ending."""
        node = self.get_current_node()
        return node.title if node.is_ending else ""

    @property
    def step_count(self) -> int:
        """Number of choices made in the current adventure."""
        return self._steps