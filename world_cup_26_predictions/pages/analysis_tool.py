"""
Main entry point for the World Cup Player Analytics.
It has two tabs: Player Analytics and Team Analytics.
"""
import streamlit as st

from world_cup_26_predictions.player_analytics.player_analytics_tab import (
    run_analytics_tab,
)
from world_cup_26_predictions.team_analytics.team_analytics_tab import (
    run_team_analytics_tab,
)

def main():
    """
    Main entry point for the World Cup Player Analytics app.
    Sets up a tabbed interface with a Player Analytics and a Team Analytics tab
    """

    st.set_page_config(page_title="World Cup Player Analytics", layout="wide", page_icon="⚽")
    st.title("World Cup 2026 Player and Team Analytics")

    # Create tabs for navigation
    tabs = st.tabs(["Player Analytics", "Team Analytics"])

    with tabs[0]:
        # Displays the player analytics page
        run_analytics_tab()

    with tabs[1]:
        run_team_analytics_tab()


if __name__ == "__main__":
    main()
