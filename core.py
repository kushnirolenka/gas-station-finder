"""Логіка застосунку «Карта АЗС» без залежності від Streamlit (ітерація v1.3).

Модуль містить формули, пошук станцій, читання даних і сервіс геокодування.
Усі функції можна перевірити автоматичними тестами без запуску інтерфейсу.
"""
import csv
import math
import time
from dataclasses import dataclass

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
def find_reachable(stations, lat, lon, fuel_left, consumption, engine_volume,
                   limit=MAX_RESULTS):
    """Найближчі станції в межах зони досяжності, до яких вистачає пального."""
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


def nearest_station(stations, lat, lon):
    """Найближча станція незалежно від запасу пального: (Station, км)."""
    return min(((s, haversine_km(lat, lon, s.latitude, s.longitude)) for s in stations),
               key=lambda pair: pair[1])


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
