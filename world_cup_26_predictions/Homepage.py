# pylint: disable=invalid-name
# This is a Page Name and its first letter should be in Capital Case.
"""
This file is the homepage for the World Cup 2026 Analysis and Predictions app.
It is the first page that users see when they visit the app. 
It provides an overview of the app's purpose and features a map of the 
host cities for the 2026 World Cup.
"""

import json

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd


def log_to_console(message: str) -> None:
    """Log a message to the browser's console using JavaScript."""
    js_code = f"""
<script>
    console.log({json.dumps(message)});
</script>
"""
    components.html(js_code)


st.set_page_config(
    page_title="Homepage",
    page_icon="👋",
)
st.write("# World Cup 2026 Analysis and Predictions ⚽️")

st.sidebar.success("Select an option above..")

st.markdown(
    """
    The 2026 World Cup is coming to North America! With the US (Seattle included!)
    , Mexico, and Canada all hosting matches,
    it will be an exciting and busy time across the continent. 
    If you are looking for a tool to use to explore who has
    previously performed well or look to the future and see what
    some machine learning can predict, look no further. 
    The map below shows all of the host cities.
    """
)

locations = [
    {'lat': 43.6532, 'lon': -79.3832},
    {'lat': 49.2827, 'lon': -123.1207},
    {'lat': 20.6752, 'lon': -103.3473},
    {'lat': 19.4326, 'lon': -99.1332},
    {'lat': 25.6866, 'lon': -100.3161},
    {'lat': 33.7501, 'lon': -84.3885},
    {'lat': 42.3555, 'lon': -71.0565},
    {'lat': 32.7767, 'lon': -96.7970},
    {'lat': 29.7601, 'lon': -95.3701},
    {'lat': 39.0997, 'lon': -94.5786},
    {'lat': 34.0549, 'lon': -118.2426},
    {'lat': 25.7617, 'lon': -80.1918},
    {'lat': 40.7128, 'lon': -74.0060},
    {'lat': 39.9526, 'lon': -75.1652},
    {'lat': 47.6061, 'lon': -122.3328},
    {'lat': 37.3387, 'lon': -121.8853}
]

df = pd.DataFrame(locations)
st.map(df, zoom=3)
