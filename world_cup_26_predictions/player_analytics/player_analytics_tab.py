import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# From our modules
from data_manager import load_data, create_advanced_player_stats, filter_players
import player_analytics.player_analytics as visuals


@st.cache_data
def get_player_stats():
    """
    Caches the loading and creation of advanced player stats
    to avoid re-processing on every user interaction.
    """
    dfs = load_data()
    return create_advanced_player_stats(dfs)


def run_analytics_tab():
    """
    Displays a Player Analytics page with:
      - Filters (gender, continent, position)
      - Key Leaderboards
      - Extra analytics
      - Two-Player Comparison (Side-by-side metrics + Radar)
      - Misc. Fun/Trivia
    """

    # --- HELPER: Dynamic Default Players ---
    def get_default_two_players(gender, all_names):
        """
        Returns up to 2 default player names that exist in 'all_names'.
        If the candidate defaults aren't available, fallback to
        the first two players in 'all_names' if possible.
        """
        # Define some candidate defaults based on gender
        if gender == "Women":
            candidate = ["Marta", "Megan Rapinoe", "Alex Morgan"]
        elif gender == "Men":
            candidate = ["Lionel Messi", "Cristiano Ronaldo", "Pelé"]
        else:
            candidate = ["Lionel Messi", "Cristiano Ronaldo"]

        # Intersect with available
        intersected = [p for p in candidate if p in all_names]
        if len(intersected) >= 2:
            return intersected[:2]
        elif len(all_names) >= 2:
            # Fallback to first two from the dataset
            return all_names[:2]
        elif len(all_names) == 1:
            return all_names
        else:
            return []  # no available players

    # ----------------------------------------------
    # 1) LOAD DATA
    # ----------------------------------------------
    st.header("Player Analytics")
    player_stats = get_player_stats()

    # ----------------------------------------------
    # 2) FILTERS
    # ----------------------------------------------
    with st.expander("Filters", expanded=False):
        gender_option = st.selectbox("Filter by Gender:", ["All", "Men", "Women"], index=0)

        # We gather continents from the entire dataset
        continent_list = ["All"] + sorted(player_stats['continent'].unique().tolist())
        continent_option = st.selectbox("Filter by Continent:", continent_list, index=0)

        position_option = st.selectbox(
            "Filter by Position:",
            ["All", "Goalkeeper", "Defender", "Midfielder", "Forward"],
            index=0
        )

    filtered_stats = filter_players(player_stats, gender_option, continent_option, position_option)
    if filtered_stats.empty:
        st.warning("No data found for the selected filters.")
        return

    # How many players to show in the various leaderboards
    top_n = st.slider("Number of Players in Top Lists:", 5, 30, 10)

    # ----------------------------------------------
    # 3) KEY LEADERBOARDS & METRICS
    # ----------------------------------------------
    st.subheader("Key Leaderboards & Metrics")

    col_left, col_right = st.columns(2)
    with col_left:
        # Top Scorers
        fig_scorers = visuals.plot_top_scorers(
            filtered_stats, n=top_n, color_by='continent',
            hover_cols=["primary_confederation", "total_appearances", "primary_team_name"]
        )
        if fig_scorers:
            st.plotly_chart(fig_scorers, use_container_width=True)

        # Top Knockout
        fig_knockout = visuals.plot_top_knockout_scorers(
            filtered_stats, n=top_n, color_by='continent',
            hover_cols=["primary_confederation","total_appearances"]
        )
        if fig_knockout:
            st.plotly_chart(fig_knockout, use_container_width=True)

    with col_right:
        # Goals per Appearance
        fig_gpa = visuals.plot_goals_per_appearance(
            filtered_stats, min_appearances=10, n=top_n,
            color_by='continent',
            hover_cols=["primary_confederation","total_goals","total_appearances"]
        )
        if fig_gpa:
            st.plotly_chart(fig_gpa, use_container_width=True)

        # Most Awarded
        fig_awards = visuals.plot_most_awarded_players(
            filtered_stats, n=top_n, color_by='continent',
            hover_cols=["primary_confederation", "total_awards"]
        )
        if fig_awards:
            st.plotly_chart(fig_awards, use_container_width=True)

    # ----------------------------------------------
    # 4) ADDITIONAL LEADERBOARDS & POSITION STATS
    # ----------------------------------------------
    with st.expander("Show More Analytics", expanded=False):
        col_ex1, col_ex2 = st.columns(2)

        with col_ex1:
            # Penalty Conversion
            fig_pen = visuals.plot_best_penalty_conversion(
                filtered_stats, min_attempts=3, n=top_n,
                color_by='continent',
                hover_cols=["primary_confederation","penalty_attempts","penalty_converted"]
            )
            if fig_pen:
                st.plotly_chart(fig_pen, use_container_width=True)

            # Highest Card Rate
            fig_cards = visuals.plot_highest_card_rate(
                filtered_stats, min_appearances=10, n=top_n,
                color_by='continent',
                hover_cols=["primary_confederation","total_cards","total_appearances"]
            )
            if fig_cards:
                st.plotly_chart(fig_cards, use_container_width=True)

        with col_ex2:
            # Substitution Patterns
            fig_on, fig_off = visuals.plot_substitution_patterns(
                filtered_stats, n=top_n, color_by='continent'
            )
            if fig_on:
                st.plotly_chart(fig_on, use_container_width=True)
            if fig_off:
                st.plotly_chart(fig_off, use_container_width=True)

        st.subheader("Position-Specific Leaderboards")
        cp1, cp2 = st.columns(2)
        with cp1:
            fig_gk = visuals.plot_position_appearances(filtered_stats,
                        position_bool_column='goal_keeper',
                        position_label='Goalkeepers', n=top_n,
                        color_by='continent', hover_cols=["primary_confederation","total_appearances"])
            if fig_gk:
                st.plotly_chart(fig_gk, use_container_width=True)

            fig_df = visuals.plot_position_appearances(filtered_stats,
                        position_bool_column='defender',
                        position_label='Defenders', n=top_n,
                        color_by='continent', hover_cols=["primary_confederation","total_appearances"])
            if fig_df:
                st.plotly_chart(fig_df, use_container_width=True)

        with cp2:
            fig_mf = visuals.plot_position_appearances(filtered_stats,
                        position_bool_column='midfielder',
                        position_label='Midfielders', n=top_n,
                        color_by='continent', hover_cols=["primary_confederation","total_appearances"])
            if fig_mf:
                st.plotly_chart(fig_mf, use_container_width=True)

            fig_fw = visuals.plot_position_appearances(filtered_stats,
                        position_bool_column='forward',
                        position_label='Forwards', n=top_n,
                        color_by='continent', hover_cols=["primary_confederation","total_appearances"])
            if fig_fw:
                st.plotly_chart(fig_fw, use_container_width=True)

    # ----------------------------------------------
    # 5) TWO-PLAYER COMPARISON
    # ----------------------------------------------
    st.markdown("---")
    st.subheader("Two-Player Comparison")

    # Create a dynamic default for the 2 players, based on the filtered list
    all_names = sorted(filtered_stats['full_name'].unique().tolist())
    default_two = get_default_two_players(gender_option, all_names)

    selected_two = st.multiselect(
        "Select Exactly 2 Players",
        all_names,
        default=default_two,
        max_selections=2
    )

    if len(selected_two) < 2:
        # If user has not chosen 2 players, show info
        st.info("Please select exactly 2 players.")
    else:
        # Now we have 2 players selected
        comparison_df = visuals.compare_players(filtered_stats, selected_two)
        if comparison_df.empty or len(comparison_df) < 2:
            st.warning("No data or insufficient data to compare these players.")
        else:
            # 3-column layout: left, center, right
            col_p1, col_radar, col_p2 = st.columns([2,3,2])

            # We'll show 5 core stats
            p1 = comparison_df.iloc[0]
            p2 = comparison_df.iloc[1]

            with col_p1:
                st.markdown(f"<h3 style='text-align:center'>{p1['full_name']}</h3>", unsafe_allow_html=True)
                st.metric("Appearances", f"{int(p1['total_appearances'])}")
                st.metric("Total Goals", f"{int(p1['total_goals'])}")
                st.metric("Knockout Goals", f"{int(p1['knockout_goals'])}")
                st.metric("Total Cards", f"{int(p1['total_cards'])}")
                st.metric("Total Awards", f"{int(p1['total_awards'])}")

            with col_p2:
                st.markdown(f"<h3 style='text-align:center'>{p2['full_name']}</h3>", unsafe_allow_html=True)
                st.metric("Appearances", f"{int(p2['total_appearances'])}")
                st.metric("Total Goals", f"{int(p2['total_goals'])}")
                st.metric("Knockout Goals", f"{int(p2['knockout_goals'])}")
                st.metric("Total Cards", f"{int(p2['total_cards'])}")
                st.metric("Total Awards", f"{int(p2['total_awards'])}")

            # Center: radar
            with col_radar:
                radar_fig = visuals.plot_comparison_radar(filtered_stats, selected_two)
                if radar_fig:
                    st.plotly_chart(radar_fig, use_container_width=True)

    # ----------------------------------------------
    # 6) CLUTCH & IMPACT
    # ----------------------------------------------
    st.markdown("---")
    st.subheader("Clutch Scorers & Impact Players")

    c1, c2 = st.columns(2)
    with c1:
        fig_clutch = visuals.plot_top_clutch_scorers(filtered_stats, n=5)
        if fig_clutch:
            st.plotly_chart(fig_clutch, use_container_width=True)
        else:
            st.info("No data for Clutch Scorers.")

    with c2:
        fig_impact = visuals.plot_top_impact_players(filtered_stats, n=5)
        if fig_impact:
            st.plotly_chart(fig_impact, use_container_width=True)
        else:
            st.info("No data for Impact Players.")

    # ----------------------------------------------
    # 7) MEN & WOMEN TRIVIA
    # ----------------------------------------------
    st.markdown("---")
    st.subheader("Men & Women World Cup Trivia")

    st.subheader("Men's World Cup")
    colA, colB, colC, colD = st.columns(4)
    with colA:
        st.metric("🏟️ First Edition", "1930")
    with colB:
        st.metric("🗓️ Total Tournaments", "22")
    with colC:
        st.metric("🏆 Most Titles", "Brazil (5)")
    with colD:
        st.metric("👑 Current Champion", "Argentina (2022)")

    st.markdown("---")
    st.subheader("Women's World Cup")
    colW1, colW2, colW3, colW4 = st.columns(4)
    with colW1:
        st.metric("🏟️ First Edition", "1991")
    with colW2:
        st.metric("🗓️ Total Tournaments", "9")
    with colW3:
        st.metric("🏆 Most Titles", "USA (4)")
    with colW4:
        st.metric("👑 Current Champion", "Spain (2023)")

    st.markdown("---")