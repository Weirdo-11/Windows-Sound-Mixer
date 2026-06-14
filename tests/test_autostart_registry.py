import pytest

from sound_mixer.autostart.registry import AutostartManager, AutostartUnavailableError
from tests.fake_registry import FakeRegistry


@pytest.fixture
def manager() -> AutostartManager:
    return AutostartManager(app_name="SoundMixerTest", registry=FakeRegistry())


def test_initially_disabled(manager):
    assert manager.is_enabled() is False


def test_enable_then_disable(manager):
    manager.enable()
    assert manager.is_enabled() is True

    manager.disable()
    assert manager.is_enabled() is False


def test_disable_when_not_enabled_is_noop(manager):
    manager.disable()
    assert manager.is_enabled() is False


def test_enable_is_idempotent(manager):
    manager.enable()
    manager.enable()
    assert manager.is_enabled() is True


def test_unavailable_without_registry():
    manager = AutostartManager(app_name="SoundMixerTest", registry=None)

    with pytest.raises(AutostartUnavailableError):
        manager.is_enabled()
