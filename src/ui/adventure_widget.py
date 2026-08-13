"""Adventure game UI widget."""

from __future__ import annotations

import re
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.adventure import AdventureGame
from src.models.adventure_node import AdventureNode
from src.utils.sound_manager import SoundManager
from src.utils.stats_tracker import StatsTracker


class AdventureWidget(QWidget):
    """Widget for the text adventure game."""

    back_to_menu = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        stats_tracker: StatsTracker | None = None,
    ) -> None:
        """Initialize the Adventure widget.

        Args:
            parent: Optional parent widget.
            stats_tracker: Optional statistics tracker for recording endings.
        """
        super().__init__(parent)

        self._stats_tracker = stats_tracker
        self._sound = SoundManager.instance()
        self._game = AdventureGame(language="english")
        self._choice_buttons: list[QPushButton] = []
        self._ending_recorded = False
        self._loading_story = True

        self._build_ui()
        self._refresh_story_combo()
        self._update_story_info_labels()

        self._loading_story = False
        self._show_node()

    def _build_ui(self) -> None:
        """Build the widget layout and connect signals."""
        layout = QVBoxLayout(self)

        title = QLabel("Adventure Quest")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #89b4fa;"
        )
        layout.addWidget(title)

        controls_row = QHBoxLayout()

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("English", "english")
        self._lang_combo.addItem("Persian", "persian")
        self._lang_combo.currentIndexChanged.connect(self._on_language_combo_changed)

        controls_row.addWidget(QLabel("Language:"))
        controls_row.addWidget(self._lang_combo)

        self._story_combo = QComboBox()
        self._story_combo.currentIndexChanged.connect(self._on_story_combo_changed)

        controls_row.addWidget(QLabel("Story File:"))
        controls_row.addWidget(self._story_combo, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        controls_row.addWidget(refresh_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.clicked.connect(self._on_restart_clicked)
        controls_row.addWidget(restart_btn)

        layout.addLayout(controls_row)

        info_row = QHBoxLayout()

        self._story_name_label = QLabel("Story: Built-in / Default")
        self._story_name_label.setStyleSheet("font-size: 12px; color: #a6e3a1;")

        self._language_label = QLabel("Language: English")
        self._language_label.setStyleSheet("font-size: 12px; color: #89b4fa;")

        info_row.addWidget(self._story_name_label)
        info_row.addStretch(1)
        info_row.addWidget(self._language_label)

        layout.addLayout(info_row)

        self._scene_label = QLabel("")
        self._scene_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #f9e2af;"
        )
        layout.addWidget(self._scene_label)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setStyleSheet("font-size: 14px;")
        layout.addWidget(self._text_edit, 1)

        self._inventory_label = QLabel("Inventory: (empty)")
        self._inventory_label.setStyleSheet("font-size: 12px; color: #a6adc8;")
        layout.addWidget(self._inventory_label)

        self._choices_layout = QVBoxLayout()
        layout.addLayout(self._choices_layout)

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_btn)

    def _on_language_combo_changed(self, index: int) -> None:
        """Handle language selection."""
        if self._loading_story:
            return

        language = self._current_language()

        if self._game.story_name:
            self._game.language = language
            self._update_story_info_labels()
            self._show_node()
        else:
            self._sound.play_click()
            self._ending_recorded = False
            self._game.set_language(language)
            self._update_story_info_labels()
            self._show_node()

    def _on_story_combo_changed(self, index: int) -> None:
        """Handle story file selection."""
        if self._loading_story:
            return

        story_name = self._story_combo.currentData()
        language = self._current_language()

        self._sound.play_click()
        self._ending_recorded = False

        if story_name:
            inferred_language = self._infer_language_from_story_name(story_name)
            if inferred_language:
                language = inferred_language

            self._game.set_story(str(story_name), language)
        else:
            self._game.set_language(language)

        self._sync_language_combo_to(self._game.language)
        self._update_story_info_labels()
        self._show_node()

    def _on_refresh_clicked(self) -> None:
        """Refresh the list of available story files."""
        self._sound.play_click()
        self._refresh_story_combo()
        self._update_story_info_labels()

    def _on_restart_clicked(self) -> None:
        """Restart the current adventure."""
        self._sound.play_click()
        self._ending_recorded = False
        self._game.start()
        self._show_node()

    def _on_back_clicked(self) -> None:
        """Return to the main menu."""
        self._sound.play_click()
        self.back_to_menu.emit()

    def _refresh_story_combo(self) -> None:
        """Load story file names from data/adventure into the combo box."""
        self._loading_story = True

        current_story = self._game.story_name or ""

        self._story_combo.clear()
        self._story_combo.addItem("Built-in / Default", "")

        try:
            story_names = AdventureGame.get_available_story_names()
        except AttributeError:
            story_names = []

        for name in story_names:
            self._story_combo.addItem(f"{name}.json", name)

        index = self._story_combo.findData(current_story)

        if index >= 0:
            self._story_combo.setCurrentIndex(index)
        else:
            self._story_combo.setCurrentIndex(0)

        self._loading_story = False

    def _sync_language_combo_to(self, language: str) -> None:
        """Synchronize the language combo without triggering reloads."""
        self._loading_story = True

        index = self._lang_combo.findData(language)
        if index >= 0:
            self._lang_combo.setCurrentIndex(index)

        self._loading_story = False

    def _current_language(self) -> str:
        """Return the currently selected language code."""
        language = self._lang_combo.currentData()

        if not language:
            language = self._lang_combo.currentText().lower()

        return str(language)

    def _update_story_info_labels(self) -> None:
        """Update visible story name and language labels."""
        if self._game.story_name:
            story_display = self._story_file_display(self._game.story_name)
        else:
            story_display = "Built-in / Default"

        self._story_name_label.setText(f"Story: {story_display}")

        if self._game.language in {"persian", "farsi", "fa"}:
            language_display = "Persian"
        else:
            language_display = "English"

        self._language_label.setText(f"Language: {language_display}")

    def _story_file_display(self, story_name: str) -> str:
        """Return a displayable JSON file name."""
        name = Path(str(story_name)).name

        if not name.lower().endswith(".json"):
            name = f"{name}.json"

        return name

    def _infer_language_from_story_name(self, story_name: str) -> str | None:
        """Infer language from the story file name if possible."""
        parts = re.split(r"[^a-z0-9]+", str(story_name).lower())
        parts = [part for part in parts if part]

        if "persian" in parts or "farsi" in parts or "fa" in parts:
            return "persian"

        if "english" in parts or "en" in parts:
            return "english"

        return None

    def _show_node(self) -> None:
        """Display the current adventure node and its choices."""
        node = self._game.get_current_node()

        self._scene_label.setText(node.title)
        self._text_edit.setPlainText(node.text)

        is_rtl = self._game.language in {"persian", "farsi", "fa"}
        direction = Qt.RightToLeft if is_rtl else Qt.LeftToRight

        self._scene_label.setLayoutDirection(direction)
        self._text_edit.setLayoutDirection(direction)

        inv = self._game.inventory
        self._inventory_label.setText(
            f"Inventory: {', '.join(inv) if inv else '(empty)'}"
        )

        self._update_story_info_labels()

        for btn in self._choice_buttons:
            btn.deleteLater()
        self._choice_buttons.clear()

        choices = self._game.get_available_choices()

        for i, choice in enumerate(choices):
            btn = QPushButton(choice.text)
            btn.setLayoutDirection(direction)
            btn.clicked.connect(lambda _, idx=i: self._make_choice(idx))

            self._choices_layout.addWidget(btn)
            self._choice_buttons.append(btn)

        if node.is_ending:
            for btn in self._choice_buttons:
                btn.setEnabled(False)

            self._record_ending_if_needed(node)

    def _make_choice(self, idx: int) -> None:
        """Handle a player choice."""
        self._sound.play_move()
        self._game.make_choice(idx)
        self._show_node()

    def _record_ending_if_needed(self, node: AdventureNode) -> None:
        """Record adventure endings in statistics once per session."""
        if self._ending_recorded:
            return

        self._ending_recorded = True

        if self._is_positive_ending(node):
            self._sound.play_win()
            if self._stats_tracker is not None:
                self._stats_tracker.record_win("adventure", 100)
        else:
            self._sound.play_lose()
            if self._stats_tracker is not None:
                self._stats_tracker.record_loss("adventure")

    def _is_positive_ending(self, node: AdventureNode) -> bool:
        """Use simple keywords to decide whether an ending is positive."""
        combined = f"{node.id} {node.title} {node.text}".lower()

        positive_keywords = (
            "treasure",
            "win",
            "wins",
            "won",
            "victory",
            "success",
            "complete",
            "completed",
            "گنج",
            "پیروز",
            "موفق",
        )
        negative_keywords = (
            "lost",
            "lose",
            "loses",
            "death",
            "dead",
            "fail",
            "failed",
            "گم",
            "شکست",
            "مرگ",
        )

        if any(keyword in combined for keyword in positive_keywords):
            return True

        if any(keyword in combined for keyword in negative_keywords):
            return False

        return True