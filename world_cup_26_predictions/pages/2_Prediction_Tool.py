import streamlit as st
from predictions.predictions_app import run_prediction_app

st.set_page_config(page_title="World Cup Prediction", page_icon="⚽", layout="wide")
st.markdown("# World Cup 2026 Prediction Tool")
st.sidebar.header("Prediction Tool")
st.sidebar.markdown("""
    Use this tool to predict match outcomes for the 2026 World Cup. 
    Select teams, their historical World Cup years, and match conditions.
""")
run_prediction_app()
