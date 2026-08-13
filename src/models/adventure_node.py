"""Adventure story node model."""

from dataclasses import dataclass, field


@dataclass
class Choice:
    """A single choice in an adventure node.

    Attributes:
        text: Display text for the choice.
        next: ID of the next node.
        requires_item: Optional item required to choose this option.
    """

    text: str
    next: str
    requires_item: str | None = None

    def to_dict(self) -> dict:
        d = {"text": self.text, "next": self.next}
        if self.requires_item:
            d["requires_item"] = self.requires_item
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Choice":
        return cls(
            text=data["text"],
            next=data["next"],
            requires_item=data.get("requires_item"),
        )


@dataclass
class AdventureNode:
    """A node in the adventure story graph.

    Attributes:
        id: Unique node identifier.
        title: Node display title.
        text: Narrative text.
        choices: Available choices.
        is_ending: Whether this node ends the game.
        requires_item: Optional item needed to enter this node.
        items_available: Items the player can pick up here.
    """

    id: str
    title: str
    text: str
    choices: list[Choice] = field(default_factory=list)
    is_ending: bool = False
    requires_item: str | None = None
    items_available: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "choices": [c.to_dict() for c in self.choices],
            "is_ending": self.is_ending,
            "requires_item": self.requires_item,
            "items_available": self.items_available,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AdventureNode":
        return cls(
            id=data["id"],
            title=data["title"],
            text=data["text"],
            choices=[Choice.from_dict(c) for c in data.get("choices", [])],
            is_ending=data.get("is_ending", False),
            requires_item=data.get("requires_item"),
            items_available=data.get("items_available", []),
        )
