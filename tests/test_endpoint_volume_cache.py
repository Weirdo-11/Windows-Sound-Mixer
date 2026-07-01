import pytest

from sound_mixer.audio.pycaw_backend import ENDPOINT_TTL_S, _EndpointVolumeCache


class FakeEndpoint:
    def __init__(self, value: float = 0.5) -> None:
        self.value = value


def make_cache():
    clock = [0.0]
    endpoints = []

    def acquire():
        endpoint = FakeEndpoint()
        endpoints.append(endpoint)
        return endpoint

    cache = _EndpointVolumeCache(acquire, now=lambda: clock[0])
    return cache, clock, endpoints


def test_acquires_once_and_reuses_within_ttl():
    cache, clock, endpoints = make_cache()

    for _ in range(10):
        cache.call(lambda ep: ep.value)

    assert len(endpoints) == 1


def test_reacquires_after_ttl_elapses():
    cache, clock, endpoints = make_cache()

    cache.call(lambda ep: ep.value)
    clock[0] += ENDPOINT_TTL_S
    cache.call(lambda ep: ep.value)

    assert len(endpoints) == 2


def test_failure_invalidates_and_retries_once():
    cache, clock, endpoints = make_cache()
    calls = []

    def flaky(ep):
        calls.append(ep)
        if len(calls) == 1:
            raise OSError("device removed")
        return ep.value

    result = cache.call(flaky)

    assert result == 0.5
    assert len(endpoints) == 2
    assert calls[0] is not calls[1]


def test_second_consecutive_failure_propagates():
    cache, clock, endpoints = make_cache()

    def always_fails(ep):
        raise OSError("device removed")

    with pytest.raises(OSError):
        cache.call(always_fails)

    assert len(endpoints) == 2


def test_invalidate_forces_fresh_acquire():
    cache, clock, endpoints = make_cache()

    cache.call(lambda ep: ep.value)
    cache.invalidate()
    cache.call(lambda ep: ep.value)

    assert len(endpoints) == 2
