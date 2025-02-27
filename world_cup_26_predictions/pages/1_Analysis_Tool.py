import streamlit as st
import time
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
import json
import plotly.express as px
from data_manager import (
    load_data,
    create_advanced_player_stats,
    filter_by_gender
)

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

countries = st.multiselect(
        "Choose countries", list(df['team_name'])
    )

dataframes = load_data()
all_stats = create_advanced_player_stats(dataframes)

gender = st.multiselect(
    "Select gender", list(("Male", "Female"))
)

# Will be refactoring this -- I know the repeated code is ugly but function > code style rn :)
names_and_ko_goals = all_stats[['full_name', 'knockout_goals', 'female']]
if not gender:
    filtered_df = names_and_ko_goals.nlargest(10, 'knockout_goals')
    figure = px.bar(filtered_df, x='full_name', y='knockout_goals', title='Top 10 scorers in World Cup history')
    st.plotly_chart(figure)
else:
    if (gender[0] != 'Female'):
        filtered_df = names_and_ko_goals[names_and_ko_goals['female'] == False]
        filtered_df = filtered_df.nlargest(10, 'knockout_goals')
        figure = px.bar(filtered_df, x='full_name', y='knockout_goals', title='Top 10 male scorers in World Cup history')
        st.plotly_chart(figure)
    else:
        filtered_df = names_and_ko_goals[names_and_ko_goals['female'] == True]
        filtered_df = filtered_df.nlargest(10, 'knockout_goals')
        figure = px.bar(filtered_df, x='full_name', y='knockout_goals', title='Top 10 female scorers in World Cup history')
        st.plotly_chart(figure)

names_and_apps = all_stats[['full_name', 'total_appearances', 'female']]
if not gender:
    filtered_df = names_and_apps.nlargest(10, 'total_appearances')
    figure2 = px.bar(filtered_df, x='full_name', y='total_appearances', title='Top 10 players with most appearances in World Cup history')
    st.plotly_chart(figure2)
else:
    if (gender[0] != 'Female'):
        filtered_df = names_and_apps[names_and_apps['female'] == False]
        filtered_df = filtered_df.nlargest(10, 'total_appearances')
        figure2 = px.bar(filtered_df, x='full_name', y='total_appearances', title='Top 10 male players with most appearances in World Cup history')
        st.plotly_chart(figure2)
    else:
        filtered_df = names_and_apps[names_and_apps['female'] == True]
        filtered_df = filtered_df.nlargest(10, 'total_appearances')
        figure2 = px.bar(filtered_df, x='full_name', y='total_appearances', title='Top 10 female players with most appearances in World Cup history')
        st.plotly_chart(figure2)