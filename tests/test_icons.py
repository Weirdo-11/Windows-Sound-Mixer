import sys

from sound_mixer.overlay.icons import load_app_icon


def test_load_app_icon_falls_back_for_empty_path(qapp):
    icon = load_app_icon("")

    assert not icon.isNull()


def test_load_app_icon_falls_back_for_nonexistent_path(qapp):
    icon = load_app_icon("C:/does/not/exist.exe")

    assert not icon.isNull()


def test_load_app_icon_returns_icon_for_existing_file(qapp):
    icon = load_app_icon(sys.executable)

    assert not icon.isNull()
