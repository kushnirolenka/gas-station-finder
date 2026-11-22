"""Тести ітерації v1.3: модуль core.py (формули, дані, пошук)."""
import math
import pytest
from geopy.distance import geodesic

import core
from core import Station
from tests.helpers import make_stations, random_queries, write_csv


def stations_from(rows):
    return [Station(*r) for r in rows]


# ----------------------------------------------------------------- формули
@pytest.mark.parametrize("a, b", [
    ((49.8397, 24.0297), (50.4501, 30.5234)),   # Львів - Київ
    ((49.8397, 24.0297), (49.8500, 24.0300)),   # близько
    ((0.0, 0.0), (0.0, 1.0)),                   # екватор
])
def test_haversine_matches_geodesic_within_half_percent(a, b):
    d = core.haversine_km(*a, *b)
    assert d == pytest.approx(geodesic(a, b).km, rel=0.005)


def test_haversine_zero_and_symmetry():
    assert core.haversine_km(49.0, 24.0, 49.0, 24.0) == 0.0
    assert core.haversine_km(49, 24, 50, 30) == pytest.approx(core.haversine_km(50, 30, 49, 24))


def test_fuel_and_radius_are_inverse():
    for fuel, c, k in [(0.25, 6.5, 1.02), (5, 8.5, 1.5)]:
        r = core.reach_radius_km(fuel, c, k)
        assert core.fuel_needed_l(r, c, k) == pytest.approx(fuel)


def test_values_from_figure_2_2():
    """Контрольні числа з рисунка 2.2: 0,25 л, дизель, k = 1,02."""
    assert core.reach_radius_km(0.25, 6.5, 1.02) == pytest.approx(3.77, abs=0.01)
    assert core.fuel_needed_l(1.66, 6.5, 1.02) == pytest.approx(0.11, abs=0.005)


def test_walking_minutes_and_url():
    assert core.walking_minutes(2.5) == 30
    url = core.directions_url(1.5, 2.5, 3.5, 4.5, "walking")
    assert "origin=1.5,2.5" in url and "destination=3.5,4.5" in url and url.endswith("walking")


# -------------------------------------------------------------------- дані
def test_load_stations_reads_named_fields(tmp_path):
    path = tmp_path / "s.csv"
    write_csv(path, make_stations(10))
    result = core.load_stations(path)
    assert len(result) == 10 and isinstance(result[0], Station)
    assert result[0].id == 1 and isinstance(result[0].rating, int)


@pytest.mark.parametrize("content, fragment", [
    (None, "не знайдено"),
    ("id,name,latitude\n1,A,49,1\n", "немає стовпців"),
    ("id,name,latitude,longitude,rating\n", "порожня"),
    ("id,name,latitude,longitude,rating\n1,A,abc,24,7\n", "Рядок 2"),
    ("id,name,latitude,longitude,rating\n1,A,95,24,7\n", "поза допустимим"),
])
def test_load_stations_reports_problems(tmp_path, content, fragment):
    path = tmp_path / "s.csv"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    with pytest.raises(core.StationDataError, match=fragment):
        core.load_stations(path)


# ------------------------------------------------------------------- пошук
def brute_force(stations, lat, lon, fuel, c, k):
    r = core.reach_radius_km(fuel, c, k)
    pairs = sorted((core.haversine_km(lat, lon, s.latitude, s.longitude), s.id) for s in stations)
    return [i for d, i in pairs if d <= r][:5]


def test_find_reachable_matches_brute_force_on_100_queries():
    stations = stations_from(make_stations())
    for lat, lon, fuel, ft, k in random_queries(100):
        c = core.FUEL_CONSUMPTION[ft]
        found = core.find_reachable_loop(stations, lat, lon, fuel, c, k)
        assert [x.station.id for x in found] == brute_force(stations, lat, lon, fuel, c, k)
        assert all(x.fuel_needed_l <= fuel + core.EPS for x in found)
        assert [x.distance_km for x in found] == sorted(x.distance_km for x in found)


def test_find_reachable_empty_when_no_fuel():
    stations = stations_from(make_stations())
    assert core.find_reachable_loop(stations, 49.84, 24.03, 0.0, 6.5, 1.0) == []


def test_nearest_station_ignores_fuel():
    stations = stations_from([(1, "A", 49.0, 24.0, 7), (2, "B", 49.5, 24.0, 8)])
    station, distance = core.nearest_station_loop(stations, 49.45, 24.0)
    assert station.id == 2 and distance == pytest.approx(5.56, abs=0.05)
