"""Логіка застосунку «Карта АЗС» без залежності від Streamlit (ітерація v1.3).

Модуль містить формули, пошук станцій, читання даних і сервіс геокодування.
Усі функції можна перевірити автоматичними тестами без запуску інтерфейсу.
"""
import csv
import math
import time
from dataclasses import dataclass

import numpy as np

from geopy.exc import (GeocoderTimedOut, GeocoderUnavailable,
                       GeocoderRateLimited, GeocoderServiceError)

EARTH_RADIUS_KM = 6371.0
EPS = 1e-9               # допуск порівняння дійсних чисел (л)
MAX_RESULTS = 5          # скільки найближчих станцій показувати
WALKING_SPEED_KMH = 5.0  # середня швидкість пішохода
FUEL_CONSUMPTION = {     # л/100 км
    "бензин": 8.5,
    "дизель": 6.5,
}


# --------------------------------------------------------------- дані (Д4)
@dataclass(frozen=True)
class Station:
    id: int
    name: str
    latitude: float
    longitude: float
    rating: int


@dataclass(frozen=True)
class Candidate:
    """Станція, до якої вистачає пального, з обчисленими величинами."""
    station: Station
    distance_km: float
    fuel_needed_l: float


class StationDataError(Exception):
    """Файл зі станціями відсутній або має неправильний формат."""


REQUIRED_COLUMNS = ("id", "name", "latitude", "longitude", "rating")


def load_stations(path):
    """Читає CSV і повертає список Station; помилки описує зрозуміло."""
    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise StationDataError(
                    f"У файлі {path} немає стовпців: {', '.join(missing)}. "
                    f"Очікується: {', '.join(REQUIRED_COLUMNS)}.")
            stations = []
            for number, row in enumerate(reader, start=2):
                try:
                    st = Station(int(row["id"]), row["name"].strip(),
                                 float(row["latitude"]), float(row["longitude"]),
                                 int(row["rating"]))
                except (TypeError, ValueError):
                    raise StationDataError(f"Рядок {number}: неправильне значення в даних.")
                if not (-90 <= st.latitude <= 90 and -180 <= st.longitude <= 180):
                    raise StationDataError(f"Рядок {number}: координати поза допустимим діапазоном.")
                stations.append(st)
    except FileNotFoundError:
        raise StationDataError(f"Файл {path} не знайдено. Перевірте, що він лежить поруч із програмою.")
    if not stations:
        raise StationDataError("База заправок порожня.")
    return stations


# ----------------------------------------------------------------- формули
def haversine_km(lat1, lon1, lat2, lon2):
    """Відстань по дузі великого кола (формули (1.6)-(1.7)), км."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def fuel_needed_l(distance_km, consumption, engine_volume):
    """Формула (2.1): потрібний обсяг пального, л."""
    return distance_km / 100 * consumption * engine_volume


def reach_radius_km(fuel_left, consumption, engine_volume):
    """Формула (2.3): радіус зони досяжності, км."""
    return fuel_left / (consumption * engine_volume) * 100


def walking_minutes(distance_km):
    return int(distance_km / WALKING_SPEED_KMH * 60)


# ------------------------------------------------------------------ пошук
def find_reachable_loop(stations, lat, lon, fuel_left, consumption, engine_volume,
                        limit=MAX_RESULTS):
    """Еталонний пошук циклом Python (алгоритм версій v1.0-v1.3).

    Залишено для перевірки нового алгоритму та вимірювань."""
    radius = reach_radius_km(fuel_left, consumption, engine_volume)
    inside = []
    for station in stations:
        distance = haversine_km(lat, lon, station.latitude, station.longitude)
        if distance <= radius:
            inside.append((distance, station))
    inside.sort(key=lambda pair: pair[0])
    result = []
    for distance, station in inside[:limit]:
        need = fuel_needed_l(distance, consumption, engine_volume)
        if need <= fuel_left + EPS:
            result.append(Candidate(station, distance, need))
    return result


def nearest_station_loop(stations, lat, lon):
    """Еталонний варіант: найближча станція циклом Python."""
    return min(((s, haversine_km(lat, lon, s.latitude, s.longitude)) for s in stations),
               key=lambda pair: pair[1])



# ------------------------------------------- пошук з NumPy (Д11, ітерація v2.0)
class StationIndex:
    """Координати станцій у масивах NumPy.

    Радіани та cos(широти) обчислюються один раз під час створення, тому
    кожен запит - це кілька операцій над масивами замість циклу Python.
    """

    def __init__(self, stations):
        self.stations = list(stations)
        self._lat = np.radians([s.latitude for s in self.stations])
        self._lon = np.radians([s.longitude for s in self.stations])
        self._cos_lat = np.cos(self._lat)

    def __len__(self):
        return len(self.stations)

    def _distances(self, lat, lon):
        phi, lam = math.radians(lat), math.radians(lon)
        a = (np.sin((self._lat - phi) / 2) ** 2
             + math.cos(phi) * self._cos_lat * np.sin((self._lon - lam) / 2) ** 2)
        return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.minimum(a, 1.0)))

    def within_radius(self, lat, lon, radius_km, limit=MAX_RESULTS):
        """До limit найближчих станцій у межах радіуса: [(км, Station), ...]."""
        d = self._distances(lat, lon)
        idx = np.flatnonzero(d <= radius_km)
        if idx.size > limit:  # частковий добір замість повного сортування
            idx = idx[np.argpartition(d[idx], limit - 1)[:limit]]
        idx = idx[np.argsort(d[idx], kind="stable")]
        return [(float(d[i]), self.stations[i]) for i in idx]

    def nearest(self, lat, lon):
        """Найближча станція незалежно від запасу пального: (Station, км)."""
        d = self._distances(lat, lon)
        i = int(np.argmin(d))
        return self.stations[i], float(d[i])


class KDStationIndex:
    """k-d дерево в тривимірних координатах на одиничній сфері (формули (1.8)-(1.10)).

    Побудова коштує O(n log n), запит майже не залежить від n. Доцільне для
    сотень тисяч станцій і багатьох запитів.
    """

    def __init__(self, stations):
        from scipy.spatial import cKDTree
        self.stations = list(stations)
        lat = np.radians([s.latitude for s in self.stations])
        lon = np.radians([s.longitude for s in self.stations])
        self._tree = cKDTree(self._xyz(lat, lon))

    @staticmethod
    def _xyz(lat, lon):
        return np.column_stack([np.cos(lat) * np.cos(lon),
                                np.cos(lat) * np.sin(lon),
                                np.sin(lat)])

    def within_radius(self, lat, lon, radius_km, limit=MAX_RESULTS):
        point = self._xyz(np.radians([lat]), np.radians([lon]))[0]
        chord_max = 2 * math.sin(min(radius_km / EARTH_RADIUS_KM, math.pi) / 2)   # (1.10)
        found = self._tree.query(point, k=min(limit, len(self.stations)),
                                 distance_upper_bound=chord_max * (1 + 1e-9))
        result = []
        for chord, i in zip(np.atleast_1d(found[0]), np.atleast_1d(found[1])):
            if i < len(self.stations) and np.isfinite(chord):
                distance = 2 * EARTH_RADIUS_KM * math.asin(min(chord / 2, 1.0))  # (1.9)
                if distance <= radius_km:
                    result.append((float(distance), self.stations[i]))
        return result


def find_reachable(index, lat, lon, fuel_left, consumption, engine_volume,
                   limit=MAX_RESULTS):
    """Найближчі станції в межах зони досяжності, до яких вистачає пального.

    index: StationIndex або KDStationIndex.
    """
    radius = reach_radius_km(fuel_left, consumption, engine_volume)
    result = []
    for distance, station in index.within_radius(lat, lon, radius, limit):
        need = fuel_needed_l(distance, consumption, engine_volume)
        if need <= fuel_left + EPS:
            result.append(Candidate(station, distance, need))
    return result


def directions_url(origin_lat, origin_lon, dest_lat, dest_lon, mode):
    return ("https://www.google.com/maps/dir/?api=1"
            f"&origin={origin_lat},{origin_lon}"
            f"&destination={dest_lat},{dest_lon}"
            f"&travelmode={mode}")


# ------------------------------------------------------------ геокодування
MIN_INTERVAL = 1.1  # с між мережевими запитами (правила використання Nominatim)

MESSAGES = {
    "empty": "Введіть адресу.",
    "not_found": "Адресу не знайдено. Уточніть місто, вулицю та номер будинку.",
    "timeout": "Сервіс геокодування не відповів вчасно. Спробуйте ще раз.",
    "rate_limit": "Забагато запитів до сервісу геокодування. Зачекайте хвилину.",
    "unavailable": "Сервіс геокодування тимчасово недоступний. Спробуйте пізніше.",
    "unknown": "Не вдалося визначити адресу через технічну помилку.",
}


class GeocodingService:
    """Обгортка над геокодером: запам'ятовує вдалі відповіді й повертає
    зрозумілі повідомлення замість винятків."""

    def __init__(self, backend, min_interval=MIN_INTERVAL,
                 clock=time.monotonic, sleep=time.sleep):
        self._backend = backend
        self._cache = {}
        self._min_interval = min_interval
        self._clock = clock
        self._sleep = sleep
        self._last_request = None
        self.network_calls = 0

    @staticmethod
    def normalize(address):
        return " ".join(address.split()).casefold()

    def _wait(self):
        if self._last_request is not None:
            left = self._min_interval - (self._clock() - self._last_request)
            if left > 0:
                self._sleep(left)

    def locate(self, address):
        """Повертає (місце, None) або (None, повідомлення про помилку)."""
        key = self.normalize(address or "")
        if not key:
            return None, MESSAGES["empty"]
        if key in self._cache:
            return self._cache[key], None
        self._wait()
        self._last_request = self._clock()
        self.network_calls += 1
        try:
            place = self._backend.geocode(address)
        except GeocoderTimedOut:
            return None, MESSAGES["timeout"]
        except GeocoderRateLimited:
            return None, MESSAGES["rate_limit"]
        except (GeocoderUnavailable, GeocoderServiceError):
            return None, MESSAGES["unavailable"]
        except Exception:
            return None, MESSAGES["unknown"]
        if place is None:
            return None, MESSAGES["not_found"]
        self._cache[key] = place  # невдалі відповіді не кешуються
        return place, None
