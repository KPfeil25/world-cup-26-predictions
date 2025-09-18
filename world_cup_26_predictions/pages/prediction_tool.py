"""
This file is the prediction tool page for the World Cup 2026 Predictions.
"""

import streamlit as st
from world_cup_26_predictions.predictions.predictions_app import run_prediction_app


def main():
    """Render the prediction tool page."""

    st.set_page_config(page_title="World Cup Prediction", page_icon="⚽", layout="wide")
    st.markdown("# World Cup 2026 Prediction Tool")
    st.sidebar.header("Prediction Tool")
    st.sidebar.markdown(
        """
        Use this tool to predict match outcomes for the 2026 World Cup.
        Select teams, their historical World Cup years, and match conditions.
        """
    )
    run_prediction_app()


if __name__ == "__main__":
    main()
