import streamlit as st
from page_functions import basic_unit_map_page, milsymbol_unit_map_page, test_page


st.set_page_config(
    page_title="MilSym Mapper",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="auto"
)

pages = [
    st.Page(milsymbol_unit_map_page, title="Milsymbol Mapper"),
    st.Page(basic_unit_map_page, title="Basic Unit Map"),
    st.Page(test_page, title="Test Page"),
]

pg = st.navigation(pages)
pg.run()
