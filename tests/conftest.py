import os
import pytest
import streamlit as st
import geopy.geocoders as gg
from tests.helpers import make_stations, write_csv


class FakeLocation:
    latitude, longitude, address = 49.8397, 24.0297, "Львів, Університетська 1"


@pytest.fixture
def app_env(tmp_path, monkeypatch):
    """Каталог з тестовим gas_stations.csv і підміною Nominatim (без мережі)."""
    calls = {"n": 0}

    class FakeNominatim:
        def __init__(self, *a, **kw):
            pass

        def geocode(self, query, **kw):
            calls["n"] += 1
            return FakeLocation()

    monkeypatch.setattr(gg, "Nominatim", FakeNominatim)
    monkeypatch.chdir(tmp_path)
    st.cache_data.clear()
    st.cache_resource.clear()

    def put(rows=None):
        write_csv(tmp_path / "gas_stations.csv", rows or make_stations())

    put()
    put.calls = calls
    return put
