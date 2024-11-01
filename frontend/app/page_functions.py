import streamlit as st
import folium
from folium.plugins import Realtime, Fullscreen
from streamlit_folium import st_folium
from utils import get_cached_units, find_centroid, add_unit_marker, fetch_units
from placeholder_data import sample_units
import requests
import pandas


def unit_map_page():
    st.title("Unit Map")

    # Fetch units from FastAPI endpoint
    # TODO: Continuously pull unit data from backend
    url = "http://localhost:8000/units"
    units = get_cached_units(url, sample_units)

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
