from PySide6.QtWidgets import QWidget

from sound_mixer.overlay.win_effects import apply_acrylic_effect


def test_apply_acrylic_effect_does_not_raise(qapp):
    widget = QWidget()

    apply_acrylic_effect(widget)
