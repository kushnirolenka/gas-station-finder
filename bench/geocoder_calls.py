"""Критерій v1.2: скільки звернень до геокодера виконує застосунок за сценарій із
25 перезапусків (адреса не змінюється). Мережа замінена лічильником.

Запуск: python bench/geocoder_calls.py <шлях до program.py>
Для v1.0: git worktree add ../v10 v1.0 && python bench/geocoder_calls.py ../v10/program.py
"""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from streamlit.testing.v1 import AppTest
import geopy.geocoders as gg
from tests.helpers import make_stations, write_csv

CALLS = {"n": 0}


class Place:
    latitude, longitude, address = 49.8397, 24.0297, "Львів"


class CountingNominatim:
    def __init__(self, *a, **kw): pass
    def geocode(self, query, **kw):
        CALLS["n"] += 1
        return Place()


gg.Nominatim = CountingNominatim
script = str(Path(sys.argv[1]).resolve())
tmp = tempfile.mkdtemp()
write_csv(os.path.join(tmp, "gas_stations.csv"), make_stations())
os.chdir(tmp)
at = AppTest.from_file(script, default_timeout=120).run()
for i in range(20):
    at.sidebar.number_input[0].set_value(1.0 + 0.5 * (i % 6)).run()
    if i % 5 == 4:
        at.sidebar.selectbox[0].select("Бензин" if i % 10 == 4 else "Дизель").run()
assert not at.exception, at.exception
print("запусків програми: 25; звернень до геокодера:", CALLS["n"])
