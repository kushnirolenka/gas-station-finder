"""Побудова карти Folium (без залежності від Streamlit)."""
import html
from functools import lru_cache

import folium


def rating_color(rating):
    if rating >= 8:
        return "green"
    if rating >= 6:
        return "blue"
    return "orange"


def marker_html(rating):
    return (f'<div style="background-color: {rating_color(rating)}; color: white; '
            'text-align: center; font-weight: bold; border-radius: 50%; width: 28px; '
            'height: 28px; display: flex; align-items: center; justify-content: center; '
            f'font-size: 12px;">{rating}</div>')


def marks_of(candidates):
    """Ключ для кешу: хешовані пари (станція, потрібне пальне, л), округлені до 0,01."""
    return tuple((c.station, round(c.fuel_needed_l, 2)) for c in candidates)


def _build(lat, lon, radius_km, marks):
    mymap = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Circle(radius=radius_km * 1000, location=[lat, lon], color="crimson",
                  fill=True, fill_color="crimson", fill_opacity=0.1,
                  popup=f"Ваша зона досяжності: {radius_km:.1f} км").add_to(mymap)
    folium.Marker([lat, lon], popup="Ваше місцезнаходження",
                  icon=folium.Icon(color="red")).add_to(mymap)
    for station, fuel in marks:
        popup = (f"<b>Назва:</b> {html.escape(station.name)}<br>"
                 f"<b>Рейтинг:</b> {station.rating}<br>"
                 f"<b>Необхідне паливо:</b> {fuel:.2f} літрів")
        folium.Marker([station.latitude, station.longitude],
                      popup=folium.Popup(popup, max_width=200),
                      icon=folium.DivIcon(html=marker_html(station.rating),
                                          icon_size=(28, 28))).add_to(mymap)
    return mymap


def build_map(lat, lon, radius_km, candidates):
    """Карта з колом досяжності, позначкою користувача й маркерами станцій."""
    return _build(lat, lon, radius_km, marks_of(candidates))


@lru_cache(maxsize=32)
def _map_html(lat, lon, radius_km, marks):
    return _build(lat, lon, radius_km, marks).get_root().render()


def map_html(lat, lon, radius_km, candidates):
    """HTML-код карти з кешем (Д9): однаковий запит не будує карту вдруге."""
    return _map_html(round(lat, 6), round(lon, 6), round(radius_km, 3), marks_of(candidates))
