"""Тести ітерації v1.1: коректність (дефекти Д1, Д2, Д6)."""
import math
from pathlib import Path
from streamlit.testing.v1 import AppTest

import core
from tests.helpers import make_stations, random_queries

APP = str(Path(__file__).resolve().parent.parent / "program.py")


def test_reach_radius_inverts_fuel_needed():
    for fuel, c, k in [(0.25, 6.5, 1.02), (5, 8.5, 1.5), (10, 6.5, 0.5)]:
        r = core.reach_radius_km(fuel, c, k)
        assert math.isclose(core.fuel_needed_l(r, c, k), fuel, rel_tol=1e-9)


def test_radius_and_fuel_agree_on_100_random_queries():
    """Критерій успіху v1.1: коло і розрахунок пального узгоджені для 100 запитів."""
    stations = make_stations()
    mismatches = 0
    for lat, lon, fuel, fuel_type, k in random_queries(100):
        c = core.FUEL_CONSUMPTION[fuel_type]
        r = core.reach_radius_km(fuel, c, k)
        for _, _, slat, slon, _ in stations:
            d = core.haversine_km(lat, lon, slat, slon)
            inside = d <= r
            reachable = core.fuel_needed_l(d, c, k) <= fuel + core.EPS
            mismatches += inside != reachable
    assert mismatches == 0


def _sidebar_text(at):
    return [m.value for m in at.sidebar.markdown]


def test_rating_is_taken_by_station_id(app_env):
    """Д1: три станції однієї мережі з різними оцінками не перезаписують одна одну."""
    app_env([(1, "WOG", 49.845, 24.0297, 9),
             (2, "WOG", 49.850, 24.0297, 5),
             (3, "WOG", 49.855, 24.0297, 7)])
    at = AppTest.from_file(APP, default_timeout=60).run()
    text = " ".join(_sidebar_text(at))
    assert "Рейтинг: 9" in text and "Рейтинг: 5" in text and "Рейтинг: 7" in text


def test_numbering_is_consecutive_and_matches_selectbox(app_env):
    """Д6: номери у списку 1..m без пропусків збігаються з варіантами вибору."""
    app_env()
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.number_input[0].set_value(5.0).run()
    numbers = [int(t.split(".")[0]) for t in _sidebar_text(at)
               if t[:1].isdigit() and t.split(".")[0].isdigit()]
    assert numbers == list(range(1, len(numbers) + 1)) and numbers
    assert at.sidebar.selectbox[1].options == [str(n) for n in numbers]


def test_app_reports_missing_data_file(app_env):
    app_env()
    import os
    os.remove("gas_stations.csv")
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert any("не знайдено" in e.value for e in at.error)
