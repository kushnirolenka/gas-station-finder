"""Карта АЗС: інтерфейс Streamlit (версія v1.3).

Уся логіка винесена в core.py і mapview.py; тут лише елементи керування
та виведення. Запуск: streamlit run program.py
"""
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static

import core
import mapview

DATA_FILE = "gas_stations.csv"


@st.cache_resource
def get_index(path):
    """Станції в масивах NumPy: створюються один раз і живуть увесь сеанс."""
    return core.StationIndex(core.load_stations(path))


@st.cache_resource
def get_geocoder():
    """Один екземпляр сервісу на весь сеанс: кеш переживає перезапуски програми."""
    return core.GeocodingService(Nominatim(user_agent="gas_station_locator_v5", timeout=5))


def read_inputs():
    fuel_type = st.sidebar.selectbox("Оберіть тип палива:", ("Дизель", "Бензин"))
    fuel_left = st.sidebar.number_input("Введіть кількість пального в баку (л):",
                                        min_value=0.0, value=1.0)
    engine_volume = st.sidebar.number_input("Введіть коефіцієнт об'єму двигуна:",
                                            min_value=0.1, value=1.0)
    address = st.sidebar.text_input("Введіть ваше місцезнаходження:",
                                    value="Львів, Університетська 1")
    return fuel_type.lower(), fuel_left, engine_volume, address


def show_candidates(candidates):
    st.sidebar.subheader("Найближчі заправки:")
    for number, c in enumerate(candidates, start=1):
        st.sidebar.write(f"{number}. {c.station.name}")
        st.sidebar.write(f"   - Відстань: {c.distance_km:.2f} км")
        st.sidebar.write(f"   - Рейтинг: {c.station.rating}")
        st.sidebar.write(f"   - Потрібно: {c.fuel_needed_l:.2f} л")


def show_walking_option(index, lat, lon):
    st.sidebar.warning("⛽ Палива не вистачає до жодної заправки!")
    station, distance = index.nearest(lat, lon)
    st.sidebar.info(
        f"🚶 Найближча заправка: **{station.name}**\n\n"
        f"📍 Відстань пішки: **{distance:.2f} км**\n\n"
        f"⏱️ Орієнтовний час: **{core.walking_minutes(distance)} хв**")
    url = core.directions_url(lat, lon, station.latitude, station.longitude, "walking")
    st.sidebar.markdown(f"[🚶 МАРШРУТ ПІШКИ У GOOGLE MAPS]({url})")


def show_route_choice(candidates, lat, lon):
    options = [str(n) for n in range(1, len(candidates) + 1)]
    chosen = st.sidebar.selectbox("Виберіть номер АЗС:", options)
    if st.sidebar.button("Прокласти маршрут"):
        target = candidates[int(chosen) - 1].station
        url = core.directions_url(lat, lon, target.latitude, target.longitude, "driving")
        st.sidebar.markdown(f"[🚀 ВІДКРИТИ МАРШРУТ У GOOGLE MAPS]({url})")


def main():
    st.title("Карта АЗС")
    st.sidebar.title("Пошук станцій")
    fuel_type, fuel_left, engine_volume, address = read_inputs()

    place, error = get_geocoder().locate(address)
    if error:
        st.sidebar.error(error)
        return
    try:
        index = get_index(DATA_FILE)
    except core.StationDataError as e:
        st.error(str(e))
        return

    consumption = core.FUEL_CONSUMPTION[fuel_type]
    lat, lon = place.latitude, place.longitude
    radius = core.reach_radius_km(fuel_left, consumption, engine_volume)
    candidates = core.find_reachable(index, lat, lon, fuel_left, consumption, engine_volume)

    folium_static(mapview.build_map(lat, lon, radius, candidates))
    show_candidates(candidates)
    if candidates:
        show_route_choice(candidates, lat, lon)
    else:
        show_walking_option(index, lat, lon)


if __name__ == "__main__":
    main()
