"""
Streamlit page for Player and Team Analytics, leveraging data_manager and player_analytics modules.
"""

import streamlit as st

# Local imports (relative import from the same package)
from data_manager import load_data, create_advanced_player_stats, filter_players
import player_analytics.player_analytics as visuals


@st.cache_data
def get_player_stats():
    """
    Caches the loading and creation of advanced player stats
    to avoid re-processing on every user interaction.
    """
    data_frames = load_data()
    return create_advanced_player_stats(data_frames)


def get_default_two_players(gender, all_names):
    """
    Returns up to 2 default player names that exist in 'all_names'.
    If the candidate defaults aren't available, fallback to
    the first two players in 'all_names' if possible.
    """
    if gender == "Women":
        candidate_defaults = ["Marta", "Megan Rapinoe", "Alex Morgan"]
    elif gender == "Men":
        candidate_defaults = ["Lionel Messi", "Cristiano Ronaldo", "Pelé"]
    else:
        candidate_defaults = ["Lionel Messi", "Cristiano Ronaldo"]

    intersected = [p for p in candidate_defaults if p in all_names]
    if len(intersected) >= 2:
        return intersected[:2]
    if len(all_names) >= 2:
        return all_names[:2]
    if len(all_names) == 1:
        return all_names
    return []


def show_filters(player_stats):
    """
    Renders gender, continent, and position filters.
    Returns selected (gender_option, continent_option, position_option).
    """
    with st.expander("Filters", expanded=False):
        gender_option = st.selectbox("Filter by Gender:", ["All", "Men", "Women"], index=0)
        continent_list = ["All"] + sorted(player_stats["continent"].unique().tolist())
        continent_option = st.selectbox("Filter by Continent:", continent_list, index=0)
        position_option = st.selectbox(
            "Filter by Position:",
            ["All", "Goalkeeper", "Defender", "Midfielder", "Forward"],
            index=0
        )
    return gender_option, continent_option, position_option


def show_leaderboards(filtered_stats, top_n):
    """
    Displays the key leaderboards in two columns:
        - Left: Top Scorers & Top Knockout Scorers
        - Right: Goals per Appearance & Most Awarded
    """
    st.subheader("Key Leaderboards & Metrics", divider="blue")
    col_left, col_right = st.columns(2)

    with col_left:
        # plot_top_scorers now only needs filtered_stats and top_n
        fig_scorers = visuals.plot_top_scorers(filtered_stats, top_n=top_n)
        if fig_scorers:
            st.plotly_chart(fig_scorers, use_container_width=True)

        # plot_top_knockout_scorers likewise
        fig_knockout = visuals.plot_top_knockout_scorers(filtered_stats, top_n=top_n)
        if fig_knockout:
            st.plotly_chart(fig_knockout, use_container_width=True)

    with col_right:
        # plot_goals_per_appearance
        fig_gpa = visuals.plot_goals_per_appearance(filtered_stats, min_appearances=10, top_n=top_n)
        if fig_gpa:
            st.plotly_chart(fig_gpa, use_container_width=True)

        # plot_most_awarded_players
        fig_awards = visuals.plot_most_awarded_players(filtered_stats, top_n=top_n)
        if fig_awards:
            st.plotly_chart(fig_awards, use_container_width=True)


def show_extra_analytics(filtered_stats, top_n):
    """
    Displays additional analytics such as:
        - Best penalty conversion
        - Highest card rate
        - Substitution patterns
        - Position-specific leaderboards
    """
    with st.expander("Show More Analytics", expanded=False):
        col_ex1, col_ex2 = st.columns(2)

        with col_ex1:
            # plot_best_penalty_conversion
            fig_pen = visuals.plot_best_penalty_conversion(
                filtered_stats, min_attempts=3, top_n=top_n
            )
            if fig_pen:
                st.plotly_chart(fig_pen, use_container_width=True)

            # plot_highest_card_rate
            fig_cards = visuals.plot_highest_card_rate(
                filtered_stats,
                min_appearances=10,
                top_n=top_n)
            if fig_cards:
                st.plotly_chart(fig_cards, use_container_width=True)

        with col_ex2:
            # plot_substitution_patterns returns two figs
            fig_on, fig_off = visuals.plot_substitution_patterns(filtered_stats, top_n=top_n)
            if fig_on:
                st.plotly_chart(fig_on, use_container_width=True)
            if fig_off:
                st.plotly_chart(fig_off, use_container_width=True)

        st.subheader("Position-Specific Leaderboards", divider="blue")
        col_pos1, col_pos2 = st.columns(2)
        with col_pos1:
            # plot_position_appearances (Goalkeepers)
            fig_gk = visuals.plot_position_appearances(
                filtered_stats,
                position_bool_column="goal_keeper",
                position_label="Goalkeepers",
                top_n=top_n
            )
            if fig_gk:
                st.plotly_chart(fig_gk, use_container_width=True)

            # plot_position_appearances (Defenders)
            fig_df = visuals.plot_position_appearances(
                filtered_stats,
                position_bool_column="defender",
                position_label="Defenders",
                top_n=top_n
            )
            if fig_df:
                st.plotly_chart(fig_df, use_container_width=True)

        with col_pos2:
            # plot_position_appearances (Midfielders)
            fig_mf = visuals.plot_position_appearances(
                filtered_stats,
                position_bool_column="midfielder",
                position_label="Midfielders",
                top_n=top_n
            )
            if fig_mf:
                st.plotly_chart(fig_mf, use_container_width=True)

            # plot_position_appearances (Forwards)
            fig_fw = visuals.plot_position_appearances(
                filtered_stats,
                position_bool_column="forward",
                position_label="Forwards",
                top_n=top_n
            )
            if fig_fw:
                st.plotly_chart(fig_fw, use_container_width=True)


def show_two_player_comparison(filtered_stats, gender_option):
    """
    Renders the two-player comparison section:
    Player pickers, side-by-side metrics, and radar plot.
    """
    st.markdown("---")
    st.subheader("Two-Player Comparison", divider="blue")

    all_names = sorted(filtered_stats["full_name"].unique().tolist())
    default_two = get_default_two_players(gender_option, all_names)

    selected_two = st.multiselect(
        "Select Exactly 2 Players",
        all_names,
        default=default_two,
        max_selections=2
    )

    if len(selected_two) < 2:
        st.info("Please select exactly 2 players.")
        return

    comparison_df = visuals.compare_players(filtered_stats, selected_two)
    if comparison_df.empty or len(comparison_df) < 2:
        st.warning("No data or insufficient data to compare these players.")
        return

    col_player_one, col_radar, col_player_two = st.columns([2, 3, 2])
    player_one = comparison_df.iloc[0]
    player_two = comparison_df.iloc[1]

    with col_player_one:
        st.markdown(
            f"<h3 style='text-align:center'>{player_one['full_name']}</h3>",
            unsafe_allow_html=True
        )
        st.metric("Appearances", f"{int(player_one['total_appearances'])}")
        st.metric("Total Goals", f"{int(player_one['total_goals'])}")
        st.metric("Knockout Goals", f"{int(player_one['knockout_goals'])}")
        st.metric("Total Cards", f"{int(player_one['total_cards'])}")
        st.metric("Total Awards", f"{int(player_one['total_awards'])}")

    with col_player_two:
        st.markdown(
            f"<h3 style='text-align:center'>{player_two['full_name']}</h3>",
            unsafe_allow_html=True
        )
        st.metric("Appearances", f"{int(player_two['total_appearances'])}")
        st.metric("Total Goals", f"{int(player_two['total_goals'])}")
        st.metric("Knockout Goals", f"{int(player_two['knockout_goals'])}")
        st.metric("Total Cards", f"{int(player_two['total_cards'])}")
        st.metric("Total Awards", f"{int(player_two['total_awards'])}")

    with col_radar:
        radar_fig = visuals.plot_comparison_radar(filtered_stats, selected_two)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)


def show_clutch_and_impact(filtered_stats):
    """
    Renders the 'Clutch Scorers & Impact Players' section.
    """
    st.markdown("---")
    st.subheader("World Cup Clutch Scorers & Impact Players", divider="blue")
    col_clutch_one, col_clutch_two = st.columns(2)

    with col_clutch_one:
        fig_clutch = visuals.plot_top_clutch_scorers(filtered_stats, top_n=5)
        if fig_clutch:
            st.plotly_chart(fig_clutch, use_container_width=True)
        else:
            st.info("No data for Clutch Scorers.")

    with col_clutch_two:
        fig_impact = visuals.plot_top_impact_players(filtered_stats, top_n=5)
        if fig_impact:
            st.plotly_chart(fig_impact, use_container_width=True)
        else:
            st.info("No data for Impact Players.")


def show_trivia():
    """
    Displays interesting player-centric World Cup trivia for men and women.
    """
    st.markdown("---")
    st.subheader("Men & Women World Cup Trivia", divider="blue")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Men's World Cup")
        st.metric("Youngest Player", "Norman Whiteside (17y, 41d)")
        st.metric("Most Appearances", "Lionel Messi (26)")
        st.metric("Top Scorer", "Miroslav Klose (16)")
        st.metric("Fastest Goal", "Hakan Sükür (11s, 2002)")
        st.metric("Oldest Player", "Essam El-Hadary (45y, 161d)")
    with col2:
        st.subheader("Women's World Cup")
        st.metric("Youngest Player", "Casey Phair (16y, 26d)")
        st.metric("Most Appearances", "Kristine Lilly (30)")
        st.metric("Top Scorer", "Marta (17)")
        st.metric("Fastest Goal", "Lena Videkull (~30s, 1991)")
        st.metric("Oldest Player", "Formiga (41y in 2019)")

    st.markdown("---")

def run_analytics_tab():
    """
    Displays a Player Analytics page with:
      - Filters (gender, continent, position)
      - Key Leaderboards
      - Extra analytics
      - Two-Player Comparison (Side-by-side metrics + Radar)
      - Misc. Fun/Trivia
    """
    st.header("Player Analytics")
    player_stats = get_player_stats()

    gender_option, continent_option, position_option = show_filters(player_stats)
    filtered_stats = filter_players(player_stats, gender_option, continent_option, position_option)
    if filtered_stats.empty:
        st.warning("No data found for the selected filters.")
        return

    top_n = st.slider("Number of Players in Top Lists:", 5, 30, 10)

    # Leaderboards
    show_leaderboards(filtered_stats, top_n)

    # Extra Analytics
    st.subheader("More Analytics", divider="blue")
    show_extra_analytics(filtered_stats, top_n)

    # Clutch & Impact
    show_clutch_and_impact(filtered_stats)

    # Two-Player Comparison
    show_two_player_comparison(filtered_stats, gender_option)
    # Trivia
    show_trivia()
