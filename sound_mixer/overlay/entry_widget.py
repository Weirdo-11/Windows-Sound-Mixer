from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSlider

from sound_mixer.mixer.model import MixerEntry
from sound_mixer.overlay.icons import DelayedTooltipButton, load_icon

BASE_ICON_PX = 16
BASE_SLIDER_HEIGHT_PX = 20


def slider_style(scale: float) -> str:
    groove_height = max(2, round(4 * scale))
    handle_size = round(14 * scale)
    return f"""
QSlider::groove:horizontal {{
    height: {groove_height}px;
    background: #555555;
    border-radius: {groove_height // 2}px;
}}
QSlider::handle:horizontal {{
    width: {handle_size}px;
    height: {handle_size}px;
    margin: -{(handle_size - groove_height) // 2}px 0;
    background: #cccccc;
    border-radius: {handle_size // 2}px;
}}
"""


class EntryWidget(QFrame):
    volume_changed = Signal(float)
    mute_toggled = Signal()
    focus_requested = Signal()
    scrolled = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("entryWidget")

        self._mute_button = DelayedTooltipButton(self)
        self._mute_button.setToolTip("Mute / unmute")
        self._mute_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._mute_button.clicked.connect(self._on_mute_clicked)

        self._label = QLabel(self)

        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(0, 100)
        self._slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._slider.valueChanged.connect(self._on_slider_changed)

        layout = QHBoxLayout(self)
        layout.addWidget(self._mute_button)
        layout.addWidget(self._label, 1)
        layout.addWidget(self._slider, 2)

    def apply_scale(self, scale: float) -> None:
        icon_px = round(BASE_ICON_PX * scale)
        self._mute_button.setIconSize(QSize(icon_px, icon_px))
        self._slider.setStyleSheet(slider_style(scale))
        self._slider.setMinimumHeight(round(BASE_SLIDER_HEIGHT_PX * scale))

    def set_entry(self, entry: MixerEntry, focused: bool) -> None:
        self._label.setText(entry.display_name)
        self._mute_button.setIcon(load_icon("muted" if entry.muted else "volume"))

        self._slider.blockSignals(True)
        self._slider.setValue(round(entry.volume * 100))
        self._slider.blockSignals(False)

        self.setProperty("focused", focused)
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_slider_changed(self, value: int) -> None:
        self.focus_requested.emit()
        self.volume_changed.emit(value / 100)

    def _on_mute_clicked(self) -> None:
        self.focus_requested.emit()
        self.mute_toggled.emit()

    def mousePressEvent(self, event) -> None:
        self.focus_requested.emit()
        super().mousePressEvent(event)

    def wheelEvent(self, event) -> None:
        self.focus_requested.emit()
        self.scrolled.emit(1 if event.angleDelta().y() > 0 else -1)
