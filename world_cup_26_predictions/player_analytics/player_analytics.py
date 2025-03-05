"""
A collection of Plotly-based functions for visualizing player statistics.
"""

import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Use a more colorful Plotly template
pio.templates.default = "plotly"

# Color sequence
DEFAULT_COLOR_SEQ = px.colors.qualitative.Bold

# Dictionary to give columns user-friendly labels in Plotly hovers and axes
LABELS = {
    "full_name": "Player",
    "total_goals": "Goals",
    "knockout_goals": "Knockout Goals",
    "goals_per_appearance": "Goals/App",
    "total_appearances": "Appearances",
    "cards_per_appearance": "Cards/App",
    "penalty_attempts": "PK Attempts",
    "penalty_conversion": "PK Conversion",
    "total_awards": "Awards",
    "times_subbed_on": "Times Subbed On",
    "times_subbed_off": "Times Subbed Off",
    "subbed_on_goals": "Subbed-On Goals",
    "clutch_goals": "Clutch Goals"
}


def plot_top_scorers(player_stats, top_n=10, color_by=None,
                     hover_cols=None, color_seq=None):
    """
    Bar chart of top scorers by total_goals.
    Returns None if:
      - necessary columns are missing
      - DataFrame is empty
    """
    required_cols = ["full_name", "total_goals"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["total_goals"] = pd.to_numeric(player_stats["total_goals"], errors="coerce")
    if player_stats["total_goals"].dropna().empty:
        return None

    df_top = player_stats.dropna(subset=["total_goals"]).nlargest(top_n, "total_goals")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="total_goals",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} All-Time Scorers",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Total Goals")
    return fig


def plot_top_knockout_scorers(player_stats, top_n=10, color_by=None,
                              hover_cols=None, color_seq=None):
    """
    Bar chart of top scorers by knockout_goals.
    """
    required_cols = ["full_name", "knockout_goals"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["knockout_goals"] = pd.to_numeric(
        player_stats["knockout_goals"], errors="coerce"
    )
    if player_stats["knockout_goals"].dropna().empty:
        return None

    df_top = player_stats.dropna(subset=["knockout_goals"]).nlargest(top_n, "knockout_goals")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="knockout_goals",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Knockout-Stage Scorers",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Knockout Goals")
    return fig


def plot_goals_per_appearance(player_stats, min_appearances=10, top_n=10,
                              color_by=None, hover_cols=None, color_seq=None):
    """
    Bar chart of top players by goals_per_appearance (>= min_appearances).
    """
    required_cols = ["full_name", "goals_per_appearance", "total_appearances"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["goals_per_appearance"] = pd.to_numeric(
        player_stats["goals_per_appearance"], errors="coerce"
    )
    player_stats["total_appearances"] = pd.to_numeric(
        player_stats["total_appearances"], errors="coerce"
    )

    df_eligible = player_stats[player_stats["total_appearances"] >= min_appearances]
    if df_eligible.empty or df_eligible["goals_per_appearance"].dropna().empty:
        return None

    df_top = df_eligible.dropna(subset=["goals_per_appearance"]) \
                        .nlargest(top_n, "goals_per_appearance")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="goals_per_appearance",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Goals/App (Min {min_appearances} Apps)",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Goals/App")
    return fig


def plot_most_awarded_players(player_stats, top_n=10, color_by=None,
                              hover_cols=None, color_seq=None):
    """
    Bar chart of top players by total_awards.
    """
    required_cols = ["full_name", "total_awards"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["total_awards"] = pd.to_numeric(
        player_stats["total_awards"], errors="coerce"
    )
    if player_stats["total_awards"].dropna().empty:
        return None

    df_top = player_stats.dropna(subset=["total_awards"]).nlargest(top_n, "total_awards")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="total_awards",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Most Awarded Players",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Awards")
    return fig


def plot_best_penalty_conversion(player_stats, min_attempts=1, top_n=10,
                                 color_by=None, hover_cols=None, color_seq=None):
    """
    Bar chart of top players by penalty_conversion (>= min_attempts).
    """
    required_cols = ["full_name", "penalty_attempts", "penalty_conversion"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["penalty_attempts"] = pd.to_numeric(
        player_stats["penalty_attempts"], errors="coerce"
    )
    player_stats["penalty_conversion"] = pd.to_numeric(
        player_stats["penalty_conversion"], errors="coerce"
    )

    df_eligible = player_stats[player_stats["penalty_attempts"] >= min_attempts]
    if df_eligible.empty or df_eligible["penalty_conversion"].dropna().empty:
        return None

    df_top = df_eligible.dropna(subset=["penalty_conversion"]) \
                        .nlargest(top_n, "penalty_conversion")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="penalty_conversion",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Penalty Conversion (Min {min_attempts} Attempts)",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Conversion Rate")
    return fig


def plot_highest_card_rate(player_stats, min_appearances=10, top_n=10,
                           color_by=None, hover_cols=None, color_seq=None):
    """
    Bar chart of players with highest cards_per_appearance (>= min_appearances).
    """
    required_cols = ["full_name", "cards_per_appearance", "total_appearances"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["cards_per_appearance"] = pd.to_numeric(
        player_stats["cards_per_appearance"], errors="coerce"
    )
    player_stats["total_appearances"] = pd.to_numeric(
        player_stats["total_appearances"], errors="coerce"
    )

    df_eligible = player_stats[player_stats["total_appearances"] >= min_appearances]
    if df_eligible.empty or df_eligible["cards_per_appearance"].dropna().empty:
        return None

    df_top = df_eligible.dropna(subset=["cards_per_appearance"]) \
                        .nlargest(top_n, "cards_per_appearance")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="cards_per_appearance",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Cards/App (Min {min_appearances} Apps)",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Cards/App")
    return fig


def plot_substitution_patterns(player_stats, top_n=10, color_by=None,
                               hover_cols=None, color_seq=None):
    """
    Returns two figures (fig_on, fig_off):
      - top 'n' players by times_subbed_on
      - top 'n' players by times_subbed_off

    The user test expects: If all times_subbed_on are NaN or all times_subbed_off are NaN,
    the function should return (None, None). i.e. if EITHER side is fully NaN, do not plot anything.
    """
    required_cols = ["full_name", "times_subbed_on", "times_subbed_off"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None, None

    player_stats = player_stats.copy()
    player_stats["times_subbed_on"] = pd.to_numeric(player_stats["times_subbed_on"], errors="coerce")
    player_stats["times_subbed_off"] = pd.to_numeric(player_stats["times_subbed_off"], errors="coerce")

    if player_stats.empty:
        return None, None

    # If ANY side is entirely NaN => return None, None per the test's requirement
    # Because the test says "If times_subbed_on is all NaN => (None, None)", likewise for subbed_off
    if player_stats["times_subbed_on"].dropna().empty or player_stats["times_subbed_off"].dropna().empty:
        return None, None

    df_on = player_stats.nlargest(top_n, "times_subbed_on").copy()
    df_off = player_stats.nlargest(top_n, "times_subbed_off").copy()

    fig_on, fig_off = None, None

    if not df_on.empty:
        fig_on = px.bar(
            df_on,
            x="full_name",
            y="times_subbed_on",
            color=color_by,
            hover_data=hover_cols,
            color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
            title=f"Top {top_n} - Times Subbed On",
            labels=LABELS
        )
        fig_on.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="# Subbed On")

    if not df_off.empty:
        fig_off = px.bar(
            df_off,
            x="full_name",
            y="times_subbed_off",
            color=color_by,
            hover_data=hover_cols,
            color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
            title=f"Top {top_n} - Times Subbed Off",
            labels=LABELS
        )
        fig_off.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="# Subbed Off")

    return fig_on, fig_off


def plot_position_appearances(player_stats, position_bool_column="goal_keeper",
                              position_label="Goalkeepers", top_n=10,
                              color_by=None, hover_cols=None, color_seq=None):
    """
    Bar chart of top 'n' players in a particular position by total_appearances.
    """
    required_cols = [position_bool_column, "full_name", "total_appearances"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["total_appearances"] = pd.to_numeric(
        player_stats["total_appearances"], errors="coerce"
    )

    df_pos = player_stats[player_stats[position_bool_column].eq(True)]
    if df_pos.empty or df_pos["total_appearances"].dropna().empty:
        return None

    df_top = df_pos.dropna(subset=["total_appearances"]) \
                   .nlargest(top_n, "total_appearances")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="full_name",
        y="total_appearances",
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} {position_label} by Appearances",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title=position_label, yaxis_title="Appearances")
    return fig


def compare_players(player_stats, selected_players):
    """
    Returns a DataFrame comparing the selected players on key stats,
    sorted by total_goals desc.
    """
    needed_cols = ["full_name", "total_goals"]
    for col in needed_cols:
        if col not in player_stats.columns:
            return pd.DataFrame()

    if player_stats.empty or not selected_players:
        return pd.DataFrame()

    subset = player_stats[player_stats["full_name"].isin(selected_players)].copy()
    if subset.empty:
        return pd.DataFrame()

    subset["total_goals"] = pd.to_numeric(subset["total_goals"], errors="coerce").fillna(0)
    subset = subset.sort_values("total_goals", ascending=False)

    columns_to_show = [
        "player_id", "full_name", "continent",
        "total_appearances", "total_goals", "knockout_goals",
        "goals_per_appearance", "total_cards", "cards_per_appearance",
        "penalty_attempts", "penalty_converted", "penalty_conversion",
        "total_awards", "times_subbed_on", "times_subbed_off",
        "subbed_on_goals", "clutch_goals"
    ]
    columns_to_show = [c for c in columns_to_show if c in subset.columns]
    return subset[columns_to_show].reset_index(drop=True)


def plot_compare_players_side_by_side(player_stats, selected_players):
    """
    Creates a grouped bar chart to compare multiple players across
    several key metrics side-by-side.
    """
    if "full_name" not in player_stats.columns:
        return None

    if player_stats.empty or not selected_players:
        return None

    df_compare = player_stats[player_stats["full_name"].isin(selected_players)].copy()
    if df_compare.empty:
        return None

    if "total_goals" in df_compare.columns:
        df_compare["total_goals"] = pd.to_numeric(df_compare["total_goals"], errors="coerce").fillna(0)
        df_compare = df_compare.sort_values("total_goals", ascending=False)

    stats_of_interest = {
        "total_goals": "Total Goals",
        "knockout_goals": "Knockout Goals",
        "total_appearances": "Appearances",
        "penalty_conversion": "Penalty Conv.",
        "total_awards": "Awards"
    }

    for col in stats_of_interest:
        if col not in df_compare.columns:
            return None
        df_compare[col] = pd.to_numeric(df_compare[col], errors="coerce").fillna(0)

    records = []
    for _, row in df_compare.iterrows():
        for stat_col, stat_label in stats_of_interest.items():
            records.append({
                "Player": row["full_name"],
                "Statistic": stat_label,
                "Value": row[stat_col]
            })
    long_df = pd.DataFrame(records)
    if long_df.empty:
        return None

    fig = px.bar(
        long_df,
        x="Statistic",
        y="Value",
        color="Player",
        barmode="group",
        title="Player Comparison (Side-by-Side)",
        color_discrete_sequence=DEFAULT_COLOR_SEQ,
    )
    fig.update_layout(title_x=0.5, xaxis_title="", yaxis_title="Value")
    return fig


def plot_comparison_radar(player_stats, selected_players):
    """
    Radar chart comparing up to 5 players on 6 advanced metrics.
    """
    if "full_name" not in player_stats.columns:
        return None

    if player_stats.empty or not selected_players:
        return None

    df_radar = player_stats[player_stats["full_name"].isin(selected_players)].copy()
    if df_radar.empty:
        return None

    df_radar = df_radar.head(5)

    needed_cols = [
        "goals_per_appearance",
        "knockout_goals",
        "cards_per_appearance",
        "penalty_conversion",
        "total_awards",
        "subbed_on_goals"
    ]
    for col in needed_cols:
        if col not in df_radar.columns:
            return None
        df_radar[col] = pd.to_numeric(df_radar[col], errors="coerce").fillna(0)

    df_radar["knockout_scaled"] = df_radar["knockout_goals"].apply(math.log1p) * 5
    df_radar["discipline_score"] = 1 / (1 + df_radar["cards_per_appearance"])
    df_radar["awards_scaled"] = df_radar["total_awards"].apply(math.log1p) * 5
    df_radar["subbed_on_scaled"] = df_radar["subbed_on_goals"].apply(math.log1p) * 5

    labels = [
        "Goals/App",
        "Knockout",
        "Discipline",
        "Pen. Conv.",
        "Awards",
        "Subbed-On"
    ]

    if df_radar.empty:
        return None

    fig = go.Figure()
    for _, row in df_radar.iterrows():
        values = [
            row["goals_per_appearance"],
            row["knockout_scaled"],
            row["discipline_score"],
            row["penalty_conversion"],
            row["awards_scaled"],
            row["subbed_on_scaled"]
        ]
        fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill="toself", name=row["full_name"]))

    fig.update_layout(
        title="Player Comparison Radar",
        title_x=0.5,
        polar={"radialaxis": {"visible": True}},
        showlegend=True
    )
    return fig


def plot_top_clutch_scorers(player_stats, top_n=5, color_seq=None):
    """
    Horizontal bar chart of the top 'n' clutch scorers (goals in 75+ minute).
    """
    required_cols = ["full_name", "clutch_goals"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["clutch_goals"] = pd.to_numeric(player_stats["clutch_goals"], errors="coerce")
    if player_stats["clutch_goals"].dropna().empty:
        return None

    df_top = player_stats.dropna(subset=["clutch_goals"]).nlargest(top_n, "clutch_goals")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="clutch_goals",
        y="full_name",
        orientation="h",
        text="clutch_goals",
        color="full_name",
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Clutch Scorers (75+ min)",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Clutch Goals", yaxis_title="Player", showlegend=False)
    fig.update_traces(textposition="inside")
    return fig


def plot_top_impact_players(player_stats, top_n=5, color_seq=None):
    """
    Horizontal bar chart of the top 'n' impact players (goals scored after being subbed on).
    """
    required_cols = ["full_name", "subbed_on_goals"]
    for col in required_cols:
        if col not in player_stats.columns:
            return None

    player_stats = player_stats.copy()
    player_stats["subbed_on_goals"] = pd.to_numeric(
        player_stats["subbed_on_goals"], errors="coerce"
    )
    if player_stats["subbed_on_goals"].dropna().empty:
        return None

    df_top = player_stats.dropna(subset=["subbed_on_goals"]).nlargest(top_n, "subbed_on_goals")
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x="subbed_on_goals",
        y="full_name",
        orientation="h",
        text="subbed_on_goals",
        color="full_name",
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {top_n} Impact Players (Subbed-on Goals)",
        labels=LABELS
    )
    fig.update_layout(title_x=0.5, xaxis_title="Goals After Sub", yaxis_title="Player", showlegend=False)
    fig.update_traces(textposition="inside")
    return fig
