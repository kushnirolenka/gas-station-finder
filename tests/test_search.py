"""Тести ітерації v2.0: пошук із NumPy та k-d деревом (Д11) дає ті самі результати,
що й еталонний цикл Python."""
import random
import pytest

import core
from core import Station
from tests.helpers import make_stations, random_queries


def as_ids(candidates):
    return [c.station.id for c in candidates]


@pytest.fixture(scope="module")
def stations():
    return [Station(*r) for r in make_stations()]


@pytest.mark.parametrize("index_class", [core.StationIndex, core.KDStationIndex])
def test_index_matches_loop_on_100_queries(stations, index_class):
    index = index_class(stations)
    for lat, lon, fuel, ft, k in random_queries(100):
        c = core.FUEL_CONSUMPTION[ft]
        expected = core.find_reachable_loop(stations, lat, lon, fuel, c, k)
        found = core.find_reachable(index, lat, lon, fuel, c, k)
        assert as_ids(found) == as_ids(expected)
        for a, b in zip(found, expected):
            assert a.distance_km == pytest.approx(b.distance_km, rel=1e-9, abs=1e-9)
            assert a.fuel_needed_l == pytest.approx(b.fuel_needed_l, rel=1e-9, abs=1e-9)


@pytest.mark.parametrize("n", [1000, 20000])
def test_all_three_algorithms_agree_on_large_random_sets(n):
    rnd = random.Random(n)
    many = [Station(i, "X", rnd.uniform(44.4, 52.4), rnd.uniform(22.1, 40.2), 7)
            for i in range(n)]
    numpy_index, kd_index = core.StationIndex(many), core.KDStationIndex(many)
    for _ in range(20):
        lat, lon, fuel = rnd.uniform(46, 51), rnd.uniform(23, 38), rnd.uniform(2, 15)
        args = (lat, lon, fuel, 6.5, 1.0)
        expected = as_ids(core.find_reachable_loop(many, *args))
        assert as_ids(core.find_reachable(numpy_index, *args)) == expected
        assert as_ids(core.find_reachable(kd_index, *args)) == expected


def test_nearest_matches_loop(stations):
    index = core.StationIndex(stations)
    for lat, lon, *_ in random_queries(50):
        s1, d1 = core.nearest_station_loop(stations, lat, lon)
        s2, d2 = index.nearest(lat, lon)
        assert s1.id == s2.id and d1 == pytest.approx(d2)


@pytest.mark.parametrize("index_class", [core.StationIndex, core.KDStationIndex])
def test_empty_result_and_radius_edges(stations, index_class):
    index = index_class(stations)
    assert index.within_radius(49.84, 24.03, 0.0) == []
    assert len(index.within_radius(49.84, 24.03, 20000.0)) == core.MAX_RESULTS
    one = index_class(stations[:1])
    assert len(one.within_radius(stations[0].latitude, stations[0].longitude, 1.0)) == 1
