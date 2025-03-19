"""
Main entry point for the World Cup Player Analytics.
It has two tabs: Player Analytics and Team Analytics.
"""
import streamlit as st

from player_analytics.player_analytics_tab import run_analytics_tab

def main():
    """
    Main entry point for the World Cup Player Analytics app.
    Sets up a tabbed interface with a Player Analytics and a Team Analytics tab
    """

    st.set_page_config(page_title="World Cup Player Analytics", layout="wide")
    st.title("World Cup 2026 Player Analytics")

    # Create tabs for navigation
    tabs = st.tabs(["Player Analytics", "Team Analytics"])

    with tabs[0]:
        # Displays the player analytics page
        run_analytics_tab()

    with tabs[1]:
        st.header("Team Analytics")
        st.markdown("---")
        st.subheader("Men & Women World Cup Trivia")

        st.subheader("Men's World Cup")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("🏟️ First Edition", "1930")
        with col_b:
            st.metric("🗓️ Total Tournaments", "22")
        with col_c:
            st.metric("🏆 Most Titles", "Brazil (5)")
        with col_d:
            st.metric("👑 Current Champion", "Argentina (2022)")

        st.markdown("---")
        st.subheader("Women's World Cup")
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            st.metric("🏟️ First Edition", "1991")
        with col_w2:
            st.metric("🗓️ Total Tournaments", "9")
        with col_w3:
            st.metric("🏆 Most Titles", "USA (4)")
        with col_w4:
            st.metric("👑 Current Champion", "Spain (2023)")

        st.markdown("---")

if __name__ == "__main__":
    main()
