"""Критерій v1.1: скільки з 100 випадкових запитів мають розбіжність між колом
досяжності й розрахунком пального (формула радіуса v1.0 і v1.1).

Запуск з кореня репозиторію: python bench/radius_mismatch.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import core
from tests.helpers import make_stations, random_queries

stations = [core.Station(*r) for r in make_stations()]


def mismatches(radius_fn):
    bad_queries = inside_unreachable = reachable_outside = 0
    for lat, lon, fuel, fuel_type, k in random_queries(100):
        c = core.FUEL_CONSUMPTION[fuel_type]
        r = radius_fn(fuel, c, k)
        flag = False
        for s in stations:
            d = core.haversine_km(lat, lon, s.latitude, s.longitude)
            inside = d <= r
            reachable = core.fuel_needed_l(d, c, k) <= fuel + core.EPS
            if inside and not reachable:
                inside_unreachable += 1; flag = True
            if reachable and not inside:
                reachable_outside += 1; flag = True
        bad_queries += flag
    return bad_queries, inside_unreachable, reachable_outside


print("v1.0 (r = F / c * 100):          запитів з розбіжністю, у колі але недосяжних, досяжних але поза колом =",
      mismatches(lambda fuel, c, k: fuel / c * 100))
print("v1.1 (r = F / (c * k) * 100):    запитів з розбіжністю, у колі але недосяжних, досяжних але поза колом =",
      mismatches(core.reach_radius_km))
