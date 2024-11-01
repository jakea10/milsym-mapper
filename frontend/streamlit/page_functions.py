import streamlit as st
import folium
from folium.plugins import Realtime, Fullscreen
from streamlit_folium import st_folium
from utils import get_cached_basic_units, find_centroid, add_unit_marker, fetch_basic_units, get_affilition_from_sidc
from placeholder_data import sample_units
import requests
import pandas
import logging
from typing import List
from models import UnitFeatureModel


# Set up logging
logging.basicConfig(level=logging.INFO)


def milsymbol_unit_map_page():
    st.title("Milsym Mapper")
    
    # Fetch units from FastAPI
    @st.cache_data(ttl=60)
    def fetch_units() -> List[UnitFeatureModel]:
        url = "http://localhost:8000/units"
        try:
            response = requests.get(url)
            response.raise_for_status()
            units = [UnitFeatureModel(**data) for data in response.json()['features']]
            return units
        except requests.exceptions.RequestException as e:
            logging.warning("Request failed: %s", e)

    units: List[UnitFeatureModel] = fetch_units()

    # Display unit details in sidebar
    with st.sidebar:
        st.header("Unit Details")
        st.markdown("---")
        for unit in units:
            expander = st.expander(label=unit.properties["uniqueDesignation"])
            expander.write(f"SIDC: {unit.properties['sidc']}")
            expander.info(f"LAT: {unit.geometry.coordinates.latitude}")
            expander.info(f"LON: {unit.geometry.coordinates.longitude}")

    # Create folium map
    all_coordinates = [(unit.geometry.coordinates) for unit in units]
    start_location = find_centroid(all_coordinates)
    unit_map = folium.Map(location=start_location, zoom_start=12)

    # Map view layer control
    folium.TileLayer('OpenTopoMap').add_to(unit_map)
    folium.LayerControl().add_to(unit_map)

    # folium.GeoJson(
    #     [unit.model_dump_json() for unit in units],
    #     # units,
    #     zoom_on_click=True,
    # ).add_to(unit_map)
    icon_image_mapping = {
        "Friendly": "images/milsymbol_2525D_FRIEND_Land_Unit.png",
        "Neutral": "images/milsymbol_2525D_NEUTRAL_Land_Unit.png",
        "Unknown": "images/milsymbol_2525D_UNKNOWN_Land_Unit.png",
        "Hostile": "images/milsymbol_2525D_HOSTILE_Land_Unit.png",
    }
    for unit in units:
        icon_url = icon_image_mapping[get_affilition_from_sidc(unit.properties["sidc"])]
        icon = folium.CustomIcon(icon_image=icon_url, icon_size=(30, 30))
        folium.Marker(
            location=unit.geometry.coordinates,
            popup=f"Lat: {unit.geometry.coordinates.latitude}, Lon: {unit.geometry.coordinates.longitude}",
            icon=icon
        ).add_to(unit_map)

    Fullscreen(
        position="topright",
        title="Fullscreen mode",
        title_cancel="Exit fullscreen",
        force_separate_button=True,
    ).add_to(unit_map)

    st_folium(unit_map)


def basic_unit_map_page():
    st.title("Unit Map")

    # Fetch units from FastAPI endpoint
    # TODO: Continuously pull unit data from backend
    url = "http://localhost:8000/units"
    units = get_cached_basic_units(url, sample_units)

    # Create folium map
    all_coordinates = [(unit.latitude, unit.longitude) for unit in units]
    start_location = find_centroid(all_coordinates)
    unit_map = folium.Map(location=start_location, zoom_start=12)

    # Map view layer control
    folium.TileLayer('OpenTopoMap').add_to(unit_map)
    folium.LayerControl().add_to(unit_map)

    # Add markers for each unit
    icon_image_mapping = {
        "friendly": "images/milsymbol_2525D_FRIEND_Land_Unit.png",
        "neutral": "images/milsymbol_2525D_NEUTRAL_Land_Unit.png",
        "unknown": "images/milsymbol_2525D_UNKNOWN_Land_Unit.png",
        "hostile": "images/milsymbol_2525D_HOSTILE_Land_Unit.png",
    }

    for unit in units:
        icon_image_file = icon_image_mapping[unit.affilitation.lower()]
        add_unit_marker(unit_map, unit, icon_image_file)
        # unit.simulate_movement()

    # Display the map
    st_folium(unit_map)

    # Sidebar
    with st.sidebar:
        st.header("Unit Details")
        st.markdown("---")
        for unit in units:
            expander = st.expander(label=unit.callsign)
            expander.write(unit.affilitation.upper())
            expander.write(f"- Latitude: {unit.latitude}")
            expander.write(f"- Longitude: {unit.longitude}")


def test_page():
    st.title("Test Page")
    

    # url = "http://localhost:8000/units"
    # units = fetch_units(url)

    # # Create folium map
    # all_coordinates = [(unit.latitude, unit.longitude) for unit in units]
    # start_location = find_centroid(all_coordinates)
    # test_map = folium.Map(location=start_location, zoom_start=12)

    # # Add a Realtime layer to the map
    # # Realtime(source=url, data=fetch_units, name="Realtime Units").add_to(test_map)
    # rt = Realtime(
    #     "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/subway_stations.geojson",
    #     get_feature_id=folium.JsCode("(f) => { return f.properties.objectid; }"),
    #     point_to_layer=folium.JsCode(
    #         "(f, latlng) => { return L.circleMarker(latlng, {radius: 8, fillOpacity: 0.2})}"
    #     ),
    #     interval=10000,
    # )
    # rt.add_to(test_map)


    # # Display the map
    # st_folium(test_map)

    tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

    with tab1:
        @st.cache_data(ttl=3600)
        def fetch_geo_json_data():
            return requests.get(
                "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
            ).json()

        geo_json_data = fetch_geo_json_data()

        m = folium.Map(location=[43, -100], zoom_start=4, width=700, height=500)

        folium.GeoJson(
            geo_json_data,
            zoom_on_click=True,
            style_function=lambda feature: {
                "fillColor": "green"
                if "e" in feature["properties"]["name"].lower()
                else "orange"
            }
        ).add_to(m)

        Fullscreen(
            position="topright",
            title="Fullscreen mode",
            title_cancel="Exit fullscreen",
            force_separate_button=True,
        ).add_to(m)

        st_folium(m)

    with tab2:
        @st.cache_data(ttl=3600)
        def fetch_unemployment_data():
            return pandas.read_csv(
                "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_unemployment_oct_2012.csv"
            )
        
        unemployment = fetch_unemployment_data()
        st.write(unemployment)
