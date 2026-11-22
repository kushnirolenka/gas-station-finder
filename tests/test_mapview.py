"""Тести побудови карти (Д5: без вкладених циклів)."""
import mapview
import core
from core import Station, Candidate


def candidates(n):
    return [Candidate(Station(i, f"АЗС{i}", 49.8 + i / 100, 24.0, 5 + i % 5), 1.0 + i, 0.1 * i)
            for i in range(n)]


def test_rating_colors_thresholds():
    assert mapview.rating_color(9) == mapview.rating_color(8) == "green"
    assert mapview.rating_color(7) == mapview.rating_color(6) == "blue"
    assert mapview.rating_color(5) == "orange"


def test_map_has_one_marker_per_candidate_plus_user():
    html = mapview.build_map(49.84, 24.03, 3.8, candidates(5)).get_root().render()
    assert html.count("L.marker(") == 5 + 1
    assert html.count("L.circle(") == 1


def test_map_without_candidates_still_has_circle_and_user():
    html = mapview.build_map(49.84, 24.03, 3.8, []).get_root().render()
    assert html.count("L.marker(") == 1 and "Ваша зона досяжності: 3.8 км" in html


def test_map_html_is_cached_for_identical_query():
    mapview._map_html.cache_clear()
    first = mapview.map_html(49.84, 24.03, 3.8, candidates(5))
    second = mapview.map_html(49.84, 24.03, 3.8, candidates(5))
    info = mapview._map_html.cache_info()
    assert first is second and (info.hits, info.misses) == (1, 1)


def test_map_html_changes_when_query_changes():
    mapview._map_html.cache_clear()
    a = mapview.map_html(49.84, 24.03, 3.8, candidates(5))
    b = mapview.map_html(49.84, 24.03, 7.6, candidates(5))
    assert a != b and mapview._map_html.cache_info().misses == 2


def test_station_name_is_escaped_in_popup():
    bad = [Candidate(Station(1, "<script>x</script>", 49.8, 24.0, 7), 1.0, 0.1)]
    out = mapview.map_html(49.84, 24.03, 3.8, bad)
    assert "<script>x</script>" not in out and "&lt;script&gt;" in out
