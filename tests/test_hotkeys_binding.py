import pytest

from sound_mixer.hotkeys.binding import (
    MOD_ALT,
    MOD_CONTROL,
    MOD_WIN,
    HotkeyBinding,
    combo_to_hotkey,
    normalize_combo,
    parse_combo,
)
from sound_mixer.settings.schema import DEFAULT_HOTKEYS


def test_normalize_combo_lowercases_and_strips():
    assert normalize_combo(" Ctrl + ALT + Num5 ") == "ctrl+alt+num5"


def test_normalize_combo_empty():
    assert normalize_combo("") == ""


def test_parse_combo_returns_tokens():
    assert parse_combo("ctrl+alt+num5") == ["ctrl", "alt", "num5"]


def test_parse_combo_empty_returns_empty_list():
    assert parse_combo("") == []


def test_parse_combo_invalid_token_raises():
    with pytest.raises(ValueError):
        parse_combo("ctrl+banana")


def test_parse_combo_accepts_function_and_arrow_keys():
    assert parse_combo("ctrl+shift+f12") == ["ctrl", "shift", "f12"]
    assert parse_combo("alt+up") == ["alt", "up"]


@pytest.mark.parametrize("hotkey", DEFAULT_HOTKEYS)
def test_default_hotkeys_parse_successfully(hotkey):
    if not hotkey["enabled"] and not hotkey["combo"]:
        assert parse_combo(hotkey["combo"]) == []
    else:
        assert parse_combo(hotkey["combo"])


def test_combo_to_hotkey_converts_numpad_digit():
    modifiers, vk = combo_to_hotkey("ctrl+alt+num5")
    assert modifiers == MOD_CONTROL | MOD_ALT
    assert vk == 0x65  # VK_NUMPAD5


def test_combo_to_hotkey_converts_win_modifier_and_letter():
    modifiers, vk = combo_to_hotkey("win+s")
    assert modifiers == MOD_WIN
    assert vk == ord("S")


def test_combo_to_hotkey_requires_a_non_modifier_key():
    with pytest.raises(ValueError):
        combo_to_hotkey("ctrl+alt")


def test_combo_to_hotkey_rejects_multiple_non_modifier_keys():
    with pytest.raises(ValueError):
        combo_to_hotkey("ctrl+a+b")


@pytest.mark.parametrize("hotkey", DEFAULT_HOTKEYS)
def test_default_hotkeys_convert_successfully(hotkey):
    if not hotkey["combo"]:
        pytest.skip("empty combo")
    combo_to_hotkey(hotkey["combo"])


def test_hotkey_binding_round_trip():
    data = {"action": "toggle_overlay", "combo": "ctrl+alt+num5", "enabled": True}
    binding = HotkeyBinding.from_dict(data)

    assert binding.action == "toggle_overlay"
    assert binding.combo == "ctrl+alt+num5"
    assert binding.enabled is True
    assert binding.to_dict() == data
