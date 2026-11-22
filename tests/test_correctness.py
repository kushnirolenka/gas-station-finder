"""Тести ітерації v1.1: коректність (дефекти Д1, Д2, Д6)."""
import math
from streamlit.testing.v1 import AppTest

import program
from tests.helpers import make_stations, random_queries

APP = program.__file__


def test_reach_radius_inverts_fuel_needed():
    for fuel, c, k in [(0.25, 6.5, 1.02), (5, 8.5, 1.5), (10, 6.5, 0.5)]:
        r = program.reach_radius(fuel, c, k)
        assert math.isclose(program.calculate_fuel_needed(r, c, k), fuel, rel_tol=1e-9)


def test_radius_and_fuel_agree_on_100_random_queries():
    """Критерій успіху v1.1: коло і розрахунок пального узгоджені для 100 запитів."""
    stations = make_stations()
    mismatches = 0
    for lat, lon, fuel, fuel_type, k in random_queries(100):
        c = program.FUEL_CONSUMPTION[fuel_type]
        r = program.reach_radius(fuel, c, k)
        for _, _, slat, slon, _ in stations:
            d = program.haversine_distance(lat, lon, slat, slon)
            inside = d <= r
            reachable = program.calculate_fuel_needed(d, c, k) <= fuel + program.EPS
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
