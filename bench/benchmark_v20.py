"""Вимірювання ітерації v2.0: час пошуку (цикл v1.0, NumPy, k-d дерево) і час карти.

Запуск з кореня репозиторію: python bench/benchmark_v20.py
Тестові точки розкидані рівномірно в прямокутнику 44,4-52,4 пн. ш., 22,1-40,2 сх. д.;
запит з точки Львова, радіус 30 км, k = 5. Показник: медіана часу за кількома повтореннями.
"""
import math, os, platform, statistics as st, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np, scipy, folium
import core, mapview
from core import Station
from tests.helpers import make_stations

U = (49.8397, 24.0297)
RADIUS_KM = 30.0
CONSUMPTION = 6.5
FUEL = RADIUS_KM * CONSUMPTION / 100


def haversine_v10(lat1, lon1, lat2, lon2):
    """Функція haversine_distance з версії v1.0 (без змін у обчисленнях)."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def timeit(func, reps):
    times = []
    for _ in range(reps):
        t = time.perf_counter(); func(); times.append((time.perf_counter() - t) * 1000)
    return st.median(times)


print("Середовище:", platform.platform(), "| Python", platform.python_version(),
      "| NumPy", np.__version__, "| SciPy", scipy.__version__, "| Folium", folium.__version__)
core.KDStationIndex([Station(0, "w", 49.0, 24.0, 7)])  # прогрів: імпорт SciPy

print("\n=== Час одного запиту, мс; побудова індексу окремо ===")
for n in (85, 1000, 10000, 100000, 1000000):
    rng = np.random.default_rng(42)
    lat, lon = rng.uniform(44.4, 52.4, n), rng.uniform(22.1, 40.2, n)
    rows = [[i, "X", float(a), float(b)] for i, (a, b) in enumerate(zip(lat, lon))]   # як у v1.0
    stations = [Station(i, "X", float(a), float(b), 7) for i, (a, b) in enumerate(zip(lat, lon))]
    reps = 200 if n <= 1000 else 30 if n <= 10000 else 10 if n <= 100000 else 3

    def query_v10():
        within = []
        for s in rows:
            d = haversine_v10(U[0], U[1], s[2], s[3])
            if d <= RADIUS_KM:
                within.append((s[0], s[1], d))
        return sorted(within, key=lambda x: x[2])[:5]

    t0 = time.perf_counter(); numpy_index = core.StationIndex(stations); build_np = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter(); kd_index = core.KDStationIndex(stations); build_kd = (time.perf_counter() - t0) * 1000
    args = (U[0], U[1], FUEL, CONSUMPTION, 1.0)
    ids = [x[0] for x in query_v10()]
    assert ids == [c.station.id for c in core.find_reachable(numpy_index, *args)] \
        == [c.station.id for c in core.find_reachable(kd_index, *args)], "результати відрізняються"
    t_v10 = timeit(query_v10, reps)
    t_np = timeit(lambda: core.find_reachable(numpy_index, *args), reps * 10)
    t_kd = timeit(lambda: core.find_reachable(kd_index, *args), reps * 10)
    print(f"n={n:>8}  знайдено {len(ids)} | цикл v1.0 {t_v10:9.3f} | NumPy {t_np:8.3f} (у {t_v10 / t_np:5.1f} раза) | "
          f"k-d {t_kd:7.4f} (у {t_v10 / t_kd:7.0f} раза) | побудова: NumPy {build_np:7.1f}, k-d {build_kd:7.1f}")

print("\n=== Карта (5 маркерів), мс ===")
sample = [core.Station(*r) for r in make_stations()]
cands = core.find_reachable(core.StationIndex(sample), U[0], U[1], 20.0, 6.5, 1.0)
t_objects = timeit(lambda: mapview.build_map(U[0], U[1], 30.8, cands), 100)
t_full = timeit(lambda: mapview.build_map(U[0], U[1], 30.8, cands).get_root().render(), 100)
mapview._map_html.cache_clear(); mapview.map_html(U[0], U[1], 30.8, cands)
t_hit = timeit(lambda: mapview.map_html(U[0], U[1], 30.8, cands), 2000)
print(f"побудова об'єктів {t_objects:.2f} | побудова + HTML {t_full:.2f} | повторний запит з кешу {t_hit:.4f} "
      f"(у {t_full / t_hit:.0f} раза швидше)")
