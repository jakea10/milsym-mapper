import streamlit as st
from page_functions import unit_map_page, test_page


st.set_page_config(
    page_title="MilSym Mapper",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="auto"
)

pages = [
    st.Page(unit_map_page, title="Unit Map"),
    st.Page(test_page, title="Test Page"),
]

pg = st.navigation(pages)
pg.run()
