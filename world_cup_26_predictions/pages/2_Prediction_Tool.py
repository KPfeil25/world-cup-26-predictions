# pylint: disable=invalid-name
"""
This file uses a naming convention required by Streamlit for proper page rendering.
We intentionally deviate from the standard snake_case style, so the invalid-name
check is disabled.
"""

import streamlit as st


st.set_page_config(page_title="Prediction Tool", page_icon="📊")

st.markdown("# Prediction Tool")
st.sidebar.header("Prediction Tool")
st.write(
    """
    This is where the prediction tool will live
    """
)
