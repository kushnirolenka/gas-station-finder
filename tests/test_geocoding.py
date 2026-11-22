"""Тести ітерації v1.2: надійність геокодування (дефект Д3)."""
import pytest
from geopy.exc import (GeocoderTimedOut, GeocoderUnavailable,
                       GeocoderRateLimited, GeocoderServiceError)
from streamlit.testing.v1 import AppTest

import program
from program import GeocodingService, MESSAGES

APP = program.__file__


class Place:
    latitude, longitude = 49.84, 24.03


class Backend:
    def __init__(self, result=Place(), error=None):
        self.result, self.error, self.calls = result, error, 0

    def geocode(self, query, **kw):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def service(backend, interval=0.0):
    return GeocodingService(backend, min_interval=interval)


def test_successful_answer_is_cached():
    b = Backend()
    s = service(b)
    for _ in range(10):
        place, err = s.locate("Львів, Університетська 1")
        assert place is not None and err is None
    assert b.calls == 1


def test_cache_key_ignores_case_and_extra_spaces():
    b = Backend()
    s = service(b)
    s.locate("Львів, Університетська 1")
    s.locate("  львів,   УНІВЕРСИТЕТСЬКА 1 ")
    assert b.calls == 1


@pytest.mark.parametrize("address, backend, message", [
    ("", Backend(), "empty"),
    ("   ", Backend(), "empty"),
    (None, Backend(), "empty"),
    ("абвгд", Backend(result=None), "not_found"),
    ("Львів", Backend(error=GeocoderTimedOut("t")), "timeout"),
    ("Львів", Backend(error=GeocoderRateLimited("429")), "rate_limit"),
    ("Львів", Backend(error=GeocoderUnavailable("net")), "unavailable"),
    ("Львів", Backend(error=GeocoderServiceError("500")), "unavailable"),
    ("Львів", Backend(error=RuntimeError("boom")), "unknown"),
])
def test_every_bad_input_gives_clear_message(address, backend, message):
    place, err = service(backend).locate(address)
    assert place is None and err == MESSAGES[message]


def test_failed_lookups_are_not_cached():
    b = Backend(error=GeocoderTimedOut("t"))
    s = service(b)
    s.locate("Львів")
    s.locate("Львів")
    assert b.calls == 2


def test_pause_between_network_requests():
    now = {"t": 100.0}
    slept = []
    s = GeocodingService(Backend(), min_interval=1.1, clock=lambda: now["t"],
                         sleep=slept.append)
    s.locate("Львів")
    now["t"] += 0.1
    s.locate("Київ")
    assert slept == [pytest.approx(1.0)]


def test_app_geocodes_once_for_twenty_reruns(app_env):
    """Критерій успіху v1.2: зміна інших елементів керування не викликає запитів."""
    app_env()
    at = AppTest.from_file(APP, default_timeout=60).run()
    for i in range(20):
        at.sidebar.number_input[0].set_value(1.0 + 0.5 * (i % 6)).run()
        if i % 5 == 4:
            at.sidebar.selectbox[0].select("Бензин" if i % 10 == 4 else "Дизель").run()
    assert not at.exception
    assert app_env.calls["n"] == 1


def test_app_shows_message_for_unknown_address(app_env, monkeypatch):
    app_env()
    import geopy.geocoders as gg

    class Nothing:
        def __init__(self, *a, **kw): pass
        def geocode(self, q, **kw): return None

    monkeypatch.setattr(gg, "Nominatim", Nothing)
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.text_input[0].set_value("абвгд").run()
    assert [e.value for e in at.sidebar.error] == [MESSAGES["not_found"]]
