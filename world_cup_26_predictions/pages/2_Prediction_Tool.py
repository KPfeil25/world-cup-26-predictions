import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError

st.set_page_config(page_title="Prediction Tool", page_icon="📊")

st.markdown("# Prediction Tool")
st.sidebar.header("Prediction Tool")
st.write(
    """
    This is where the prediction tool will live
    """
)