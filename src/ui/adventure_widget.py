"""Adventure game UI widget."""

from __future__ import annotations

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

        self._build_ui()
        self._show_node()

    def _build_ui(self) -> None:
        """Build the widget layout and connect signals."""
        layout = QVBoxLayout(self)

        title = QLabel("Adventure Quest")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #89b4fa;"
        )
        layout.addWidget(title)

        settings_row = QHBoxLayout()

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("English", "english")
        self._lang_combo.addItem("Persian", "persian")
        self._lang_combo.setCurrentIndex(0)
        self._lang_combo.currentIndexChanged.connect(self._on_language_combo_changed)

        settings_row.addWidget(QLabel("Language / Story:"))
        settings_row.addWidget(self._lang_combo)

        restart_btn = QPushButton("Restart Adventure")
        restart_btn.clicked.connect(self._on_restart_clicked)
        settings_row.addWidget(restart_btn)

        layout.addLayout(settings_row)

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
        """Change the active story language and restart the adventure."""
        language = self._lang_combo.itemData(index)

        if not language:
            language = self._lang_combo.currentText().lower()

        self._sound.play_click()
        self._ending_recorded = False
        self._game.set_language(str(language))
        self._show_node()

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