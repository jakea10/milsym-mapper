from pydantic_extra_types.coordinate import Latitude, Longitude
import requests
from typing import List, Iterable, Literal
import streamlit as st
import logging
import time
from models import Unit
import folium


# Set up logging
logging.basicConfig(level=logging.INFO)


def find_centroid(coordinates: tuple[Latitude, Longitude]) -> tuple[Latitude, Longitude]:
    if not coordinates:
        return None

    lat_sum = 0
    lon_sum = 0
    count = len(coordinates)

    for lat, lon in coordinates:
        lat_sum += lat
        lon_sum += lon

    centroid = (lat_sum / count, lon_sum / count)
    return centroid


def get_affilition_from_sidc(sidc: str) -> Literal["Friendly", "Hostile", "Neutral", "Unknown"]:
    """
    Determines unit affiliation from a MIL-STD-2525D SIDC string.
    
    Parameters:
        sidc: The SIDC string
    
    Returns:
        The unit affiliation ("Friendly", "Hostile", "Neutral", or "Unknown").
    """
    if len(sidc) >= 15:
        affiliation_code = sidc[1]
        if affiliation_code == "F":
            return "Friendly"
        elif affiliation_code == "H":
            return "Hostile"
        elif affiliation_code == "N":
            return "Neutral"
        else:
            return "Unknown"
    
    return "Unknown"


def fetch_basic_units(url: str, sample_units: Iterable[Unit] | None = None) -> List[Unit]:
    """
    Fetches units from the specified API URL.

    This function attempts to retrieve a list of units from a given URL.
    If the request fails, it will retry up to 3 times with exponential backoff.
    If the response is not a valid list or if the request fails, it will return
    the provided sample units if they are given.

    Args:
        url (str): The API endpoint to fetch units from.
        sample_units (Iterable[Unit], optional): A list of sample units to return
            in case of an error or unexpected response. Defaults to None.

    Returns:
        List[Unit]: A list of validated Unit objects fetched from the API, or
        the sample units if an error occurs and they were provided. An empty
        list is returned if no sample units are given.
    """
    units: List[Unit] = []

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()

            # Validate the response structure
            if isinstance(data, list):
                units = [Unit.model_validate(unit) for unit in data]
                return units
            else:
                logging.error("Unexpected response format: %s", data)
                break  # Exit the loop; we cannot process this

        except requests.exceptions.RequestException as e:
            logging.warning("Request failed: %s", e)
            time.sleep(2 ** attempt)  # Exponential backoff

    # Return sample units only if provided
    return sample_units if sample_units is not None else []


@st.cache_data(ttl=60)  # Cache the data for 1 minute
def get_cached_basic_units(url: str = "http://localhost:8000/units", _sample_units: Iterable[Unit] | None = None) -> List[Unit]:
    """
    Retrieves units using caching for the specified API URL.

    This function is a cached wrapper around the `fetch_units` function,
    which allows for efficient retrieval of units. The cache lasts for one hour,
    and it logs the fetching process.

    Args:
        url (str, optional): The API endpoint to fetch units from. Defaults to
            "http://localhost:8000/units".
        _sample_units (Iterable[Unit], optional): A list of sample units to return
            in case of an error or unexpected response. Defaults to None.

    Returns:
        List[Unit]: A list of validated Unit objects fetched from the API, or
        the sample units if an error occurs and they were provided. An empty
        list is returned if no sample units are given.
    """
    logging.info("Fetching units...")
    return fetch_basic_units(url, _sample_units)


def add_unit_marker(map_obj, unit: Unit, icon_url: str) -> folium.Marker:
    icon = folium.CustomIcon(icon_image=icon_url, icon_size=(30, 30))
    marker = folium.Marker(
        location=[unit.latitude, unit.longitude],
        popup=unit.affilitation,
        tooltip=unit.callsign,
        icon=icon
    )
    marker.add_to(map_obj)
    return marker
