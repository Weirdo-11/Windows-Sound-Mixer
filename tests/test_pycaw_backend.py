from unittest.mock import patch

from sound_mixer.audio.pycaw_backend import PycawAudioBackend

_PATCH_SESSIONS = "sound_mixer.audio.pycaw_backend.AudioUtilities.GetAllSessions"
_PATCH_SPEAKERS = "sound_mixer.audio.pycaw_backend.AudioUtilities.GetSpeakers"


class StubEndpointVolume:
    def __init__(self, fail_times: int = 0) -> None:
        self._fail_times = fail_times

    def _maybe_fail(self):
        if self._fail_times > 0:
            self._fail_times -= 1
            raise OSError("device gone")

    def GetMasterVolumeLevelScalar(self):
        self._maybe_fail()
        return 0.7

    def GetMute(self):
        self._maybe_fail()
        return False


class StubSpeakers:
    def __init__(self, endpoint) -> None:
        self.EndpointVolume = endpoint


def test_backend_init_does_not_enumerate_sessions():
    with patch(_PATCH_SESSIONS, return_value=[]) as mock_sessions:
        backend = PycawAudioBackend()

        assert mock_sessions.call_count == 0

        backend.refresh()

        assert mock_sessions.call_count == 1


def test_backend_starts_with_no_sessions():
    with patch(_PATCH_SESSIONS, return_value=[]):
        backend = PycawAudioBackend()

    assert backend.enumerate_sessions() == []


def test_master_volume_reads_do_not_reacquire_speakers_within_ttl():
    with patch(_PATCH_SPEAKERS, return_value=StubSpeakers(StubEndpointVolume())) as mock_speakers:
        backend = PycawAudioBackend()

        for _ in range(3):
            assert backend.get_master_volume() == 0.7
            assert backend.get_master_mute() is False

    assert mock_speakers.call_count == 1


def test_master_volume_recovers_after_endpoint_error():
    with patch(_PATCH_SPEAKERS, return_value=StubSpeakers(StubEndpointVolume(fail_times=1))) as mock_speakers:
        backend = PycawAudioBackend()

        assert backend.get_master_volume() == 0.7

    assert mock_speakers.call_count == 2
