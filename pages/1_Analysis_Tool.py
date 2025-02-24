import streamlit as st
import time
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
import json

# Logging tool, purely used for debugging
def log_to_console(message: str) -> None:
    js_code = f"""
<script>
    console.log({json.dumps(message)});
</script>
"""
    components.html(js_code)
    
st.set_page_config(page_title="Analysis Tool", page_icon="📈")

st.markdown("# Analysis Tool")
st.sidebar.header("Analysis Tool")
st.write(
    """This is where the analysis will take place"""
)

df = pd.read_csv('data/teams.csv')
# log_to_console(str(df.head()))

countries = st.multiselect(
        "Choose countries", list(df['team_name'])
    )