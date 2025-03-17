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
import pydeck as pdk
import numpy as np


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
    {'lat': 43.6532, 'lon': -79.3832, 'coordinates': [43.6532, -79.3832], 'name': 'Toronto', 'stadium': 'BMO Field', 'capacity': 30000},
    {'lat': 49.2827, 'lon': -123.1207, 'coordinates': [49.2827, -123.1207], 'name': 'Vancouver', 'stadium': 'BC Place', 'capacity': 54500},
    {'lat': 20.6752, 'lon': -103.3473, 'coordinates': [20.6752, -103.3473], 'name': 'Guadalajara', 'stadium': 'Estadio Akron', 'capacity': 46632},
    {'lat': 19.4326, 'lon': -99.1332, 'coordinates': [19.4326, -99.1332], 'name': 'Mexico City', 'stadium': 'Estadio Azteca', 'capacity': 87000},
    {'lat': 25.6866, 'lon': -100.3161, 'coordinates': [25.6866, -100.3161], 'name': 'Monterrey', 'stadium': 'Estadio BBVA', 'capacity': 53500},
    {'lat': 33.7501, 'lon': -84.3885, 'coordinates': [33.7501, -84.3885], 'name': 'Atlanta', 'stadium': 'Mercedes-Benz Stadium', 'capacity': 71000},
    {'lat': 42.3555, 'lon': -71.0565, 'coordinates': [42.3555, -71.0565], 'name': 'Boston', 'stadium': 'Gillette Stadium', 'capacity': 65878},
    {'lat': 32.7767, 'lon': -96.7970, 'coordinates': [32.7767, -96.7970], 'name': 'Dallas', 'stadium': 'AT&T Stadium', 'capacity': 80000},
    {'lat': 29.7601, 'lon': -95.3701, 'coordinates': [29.7601, -95.3701], 'name': 'Houston', 'stadium': 'NRG Stadium', 'capacity': 72220},
    {'lat': 39.0997, 'lon': -94.5786, 'coordinates': [39.0997, -94.5786], 'name': 'Kansas City', 'stadium': 'Arrowhead Stadium', 'capacity': 76416},
    {'lat': 34.0549, 'lon': -118.2426, 'coordinates': [34.0549, -118.2426], 'name': 'Los Angeles', 'stadium': 'SoFi Stadium', 'capacity': 70240},
    {'lat': 25.7617, 'lon': -80.1918, 'coordinates': [25.7617, -80.1918], 'name': 'Miami', 'stadium': 'Hard Rock Stadium', 'capacity': 65326},
    {'lat': 40.7128, 'lon': -74.0060, 'coordinates': [40.7128, -74.0060], 'name': 'New York City', 'stadium': 'MetLife Stadium', 'capacity': 82500},
    {'lat': 39.9526, 'lon': -75.1652, 'coordinates': [39.9526, -75.1652], 'name': 'Philadelphia', 'stadium': 'Lincoln Financial Field', 'capacity': 69796},
    {'lat': 47.6061, 'lon': -122.3328, 'coordinates': [47.6061, -122.3328], 'name': 'Seattle', 'stadium': 'Lumen Field', 'capacity': 68740},
    {'lat': 37.3387, 'lon': -121.8853, 'coordinates': [37.3387, -121.8853], 'name': 'San Jose', 'stadium': 'Levi\'s Stadium', 'capacity': 68500}
]



chart_data = pd.DataFrame(locations)

tooltip = {
    "html": "<b>{name}</b><br>Stadium: {stadium}<br>Capacity: {capacity}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
        "fontSize": "14px",
        "padding": "5px"
    }
}

st.pydeck_chart(
    pdk.Deck(
        map_style='dark_no_labels',
        tooltip=tooltip,
        initial_view_state=pdk.ViewState(
            latitude=38.342499,
            longitude=-98.769442,
            zoom=3,
        ),
        layers=[
            pdk.Layer(
                "TextLayer",
                data=chart_data,
                get_position="[lon, lat + 0.9]",
                get_text='name',
                get_size=12,
                get_color=[255, 255, 255],
                get_angle=0,
                get_elevation=5000,
                pickable=True
            ),
            pdk.Layer(
                "HexagonLayer",
                data=chart_data,
                get_position="[lon, lat]",
                radius=50000,
                get_text='name',
            ),
        ],
    )
)
