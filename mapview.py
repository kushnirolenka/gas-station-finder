"""Побудова карти Folium (без залежності від Streamlit)."""
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


def build_map(lat, lon, radius_km, candidates):
    """Карта з колом досяжності, позначкою користувача й маркерами станцій.

    Д5: кожен кандидат уже містить свою станцію, тому вкладені цикли не потрібні.
    """
    mymap = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Circle(radius=radius_km * 1000, location=[lat, lon], color="crimson",
                  fill=True, fill_color="crimson", fill_opacity=0.1,
                  popup=f"Ваша зона досяжності: {radius_km:.1f} км").add_to(mymap)
    folium.Marker([lat, lon], popup="Ваше місцезнаходження",
                  icon=folium.Icon(color="red")).add_to(mymap)
    for c in candidates:
        s = c.station
        popup = (f"<b>Назва:</b> {s.name}<br><b>Рейтинг:</b> {s.rating}<br>"
                 f"<b>Необхідне паливо:</b> {c.fuel_needed_l:.2f} літрів")
        folium.Marker([s.latitude, s.longitude],
                      popup=folium.Popup(popup, max_width=200),
                      icon=folium.DivIcon(html=marker_html(s.rating),
                                          icon_size=(28, 28))).add_to(mymap)
    return mymap
