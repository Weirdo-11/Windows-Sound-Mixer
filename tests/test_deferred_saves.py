import json
import time

from sound_mixer.app import SETTINGS_SAVE_DELAY_MS, install_deferred_saves
from sound_mixer.settings.store import SettingsStore


def read_volume(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)["app_volumes"].get("game.exe", {}).get("volume")


def test_volume_change_persisted_after_timer_fires(qapp, tmp_path):
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.load()
    timer = install_deferred_saves(store, qapp)
    try:
        store.set_app_volume("game.exe", 0.35)

        assert read_volume(path) is None
        assert timer.isActive()

        deadline = time.monotonic() + 5.0
        while read_volume(path) != 0.35 and time.monotonic() < deadline:
            qapp.processEvents()

        assert read_volume(path) == 0.35
    finally:
        store.set_save_scheduler(None)
        qapp.aboutToQuit.disconnect(store.flush)
        timer.stop()


def test_rapid_changes_coalesce_and_persist_final_value(qapp, tmp_path):
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.load()
    timer = install_deferred_saves(store, qapp)
    try:
        for value in (0.1, 0.2, 0.3, 0.4, 0.5):
            store.set_app_volume("game.exe", value)

        store.flush()

        assert read_volume(path) == 0.5
    finally:
        store.set_save_scheduler(None)
        qapp.aboutToQuit.disconnect(store.flush)
        timer.stop()
