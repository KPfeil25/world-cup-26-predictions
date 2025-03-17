"""
Plotly-based functions for analyzing and visualizing player statistics.
"""

import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Use a white background in plots
pio.templates.default = "plotly_white"

LABELS = {
    "full_name": "Player Name",
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
    "clutch_goals": "Clutch Goals",
}

STATS_OF_INTEREST = [
    "player_id",
    "full_name",
    "continent",
    "total_appearances",
    "total_goals",
    "knockout_goals",
    "goals_per_appearance",
    "total_cards",
    "cards_per_appearance",
    "penalty_attempts",
    "penalty_converted",
    "penalty_conversion",
    "total_awards",
    "times_subbed_on",
    "times_subbed_off",
    "subbed_on_goals",
    "clutch_goals",
]


def _check_required_cols(df, cols_needed):
    """Check if all required columns exist in df."""
    for col in cols_needed:
        if col not in df.columns:
            return False
    return True


def _prepare_numeric(df, col):
    """Convert df[col] to numeric in-place, ignoring errors."""
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


def _get_top_n(df, sort_col, top_n):
    """
    Sort df by sort_col descending, return top_n rows.
    Return None if df is empty or sort_col is all NaN.
    """
    df = df.dropna(subset=[sort_col])
    if df.empty:
        return None
    return df.nlargest(top_n, sort_col)


def _bar_chart(df, x_col, y_col, title=""):
    """
    Create a bar chart with optional coloring by 'continent' if present.
    Axis labels are set via LABELS.
    """
    color_arg = "continent" if "continent" in df.columns else None
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_arg,
        title=title,
        labels=LABELS,
    )
    fig.update_layout(
        title_x=0.5,
        xaxis_title=LABELS[x_col],
        yaxis_title=LABELS[y_col],
        template="plotly_white",
        plot_bgcolor="#e5ecf6",        # Light background color
        paper_bgcolor="#e5ecf6"
    )
    return fig


def plot_top_scorers(player_stats, top_n=10):
    """Bar chart of top scorers by total_goals."""
    if not _check_required_cols(player_stats, ["full_name", "total_goals"]):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "total_goals")
    top_df = _get_top_n(df, "total_goals", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "total_goals",
                      title=f"Top {top_n} All-Time Scorers")


def plot_top_knockout_scorers(player_stats, top_n=10):
    """Bar chart of top scorers by knockout_goals."""
    if not _check_required_cols(player_stats, ["full_name", "knockout_goals"]):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "knockout_goals")
    top_df = _get_top_n(df, "knockout_goals", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "knockout_goals",
                      title=f"Top {top_n} Knockout-Stage Scorers")


def plot_goals_per_appearance(player_stats, min_appearances=10, top_n=10):
    """
    Bar chart of top players by goals_per_appearance
    (only includes players with >= min_appearances).
    """
    needed = ["full_name", "goals_per_appearance", "total_appearances"]
    if not _check_required_cols(player_stats, needed):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "goals_per_appearance")
    _prepare_numeric(df, "total_appearances")
    df = df[df["total_appearances"] >= min_appearances]
    top_df = _get_top_n(df, "goals_per_appearance", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "goals_per_appearance",
                      title=f"Top {top_n} Goals/App (Min {min_appearances} Apps)")


def plot_most_awarded_players(player_stats, top_n=10):
    """Bar chart of top players by total_awards."""
    if not _check_required_cols(player_stats, ["full_name", "total_awards"]):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "total_awards")
    top_df = _get_top_n(df, "total_awards", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "total_awards",
                      title=f"Top {top_n} Most Awarded Players")


def plot_best_penalty_conversion(player_stats, min_attempts=1, top_n=10):
    """
    Bar chart of top players by penalty_conversion
    (players must have >= min_attempts penalty kicks).
    """
    needed = ["full_name", "penalty_attempts", "penalty_conversion"]
    if not _check_required_cols(player_stats, needed):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "penalty_attempts")
    _prepare_numeric(df, "penalty_conversion")
    df = df[df["penalty_attempts"] >= min_attempts]
    top_df = _get_top_n(df, "penalty_conversion", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "penalty_conversion",
                      title=f"Top {top_n} Penalty Conversion "
                            f"(Min {min_attempts} Attempts)")


def plot_highest_card_rate(player_stats, min_appearances=10, top_n=10):
    """
    Bar chart of players with the highest cards_per_appearance
    (requires at least min_appearances).
    """
    needed = ["full_name", "cards_per_appearance", "total_appearances"]
    if not _check_required_cols(player_stats, needed):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "cards_per_appearance")
    _prepare_numeric(df, "total_appearances")
    df = df[df["total_appearances"] >= min_appearances]
    top_df = _get_top_n(df, "cards_per_appearance", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "cards_per_appearance",
                      title=f"Top {top_n} Cards/App "
                            f"(Min {min_appearances} Apps)")


def plot_substitution_patterns(player_stats, top_n=10):
    """
    Returns two bar charts:
      1) Players with most times_subbed_on
      2) Players with most times_subbed_off
    """
    needed = ["full_name", "times_subbed_on", "times_subbed_off"]
    if not _check_required_cols(player_stats, needed):
        return None, None
    df = player_stats.copy()
    _prepare_numeric(df, "times_subbed_on")
    _prepare_numeric(df, "times_subbed_off")
    if df["times_subbed_on"].dropna().empty or df["times_subbed_off"].dropna().empty:
        return None, None
    df_on = _get_top_n(df, "times_subbed_on", top_n)
    df_off = _get_top_n(df, "times_subbed_off", top_n)
    if df_on is None or df_off is None:
        return None, None
    fig_on = _bar_chart(df_on, "full_name", "times_subbed_on",
                        title=f"Top {top_n} - Times Subbed On")
    fig_off = _bar_chart(df_off, "full_name", "times_subbed_off",
                         title=f"Top {top_n} - Times Subbed Off")
    return fig_on, fig_off


def plot_position_appearances(
    player_stats,
    position_bool_column="goal_keeper",
    position_label="Goalkeepers",
    top_n=10
):
    """
    Bar chart of top players in a given position (via position_bool_column),
    sorted by total_appearances.
    """
    needed = [position_bool_column, "full_name", "total_appearances"]
    if not _check_required_cols(player_stats, needed):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "total_appearances")
    df_pos = df[df[position_bool_column].eq(True)]
    top_df = _get_top_n(df_pos, "total_appearances", top_n)
    if top_df is None or top_df.empty:
        return None
    return _bar_chart(top_df, "full_name", "total_appearances",
                      title=f"Top {top_n} {position_label} by Appearances")


def compare_players(player_stats, selected_players):
    """Return a DataFrame comparing selected players, sorted by total_goals."""
    needed_cols = ["full_name", "total_goals"]
    if not _check_required_cols(player_stats, needed_cols):
        return pd.DataFrame()
    if player_stats.empty or not selected_players:
        return pd.DataFrame()
    subset = player_stats[player_stats["full_name"].isin(selected_players)].copy()
    if subset.empty:
        return pd.DataFrame()
    _prepare_numeric(subset, "total_goals")
    subset["total_goals"] = subset["total_goals"].fillna(0)
    subset = subset.sort_values("total_goals", ascending=False)
    columns_to_show = [c for c in STATS_OF_INTEREST if c in subset.columns]
    return subset[columns_to_show].reset_index(drop=True)

def plot_compare_players_side_by_side(player_stats, selected_players):
    """
    Create a grouped bar chart comparing selected players on core stats:
    total_goals, knockout_goals, goals_per_appearance, cards_per_appearance,
    penalty_conversion, clutch_goals.
    """
    stats_mandatory = [
        "total_goals",
        "knockout_goals",
        "goals_per_appearance",
        "cards_per_appearance",
        "penalty_conversion",
        "clutch_goals",
    ]
    needed_cols = ["full_name"] + stats_mandatory
    if not _check_required_cols(player_stats, needed_cols):
        return None
    df = player_stats[player_stats["full_name"].isin(selected_players)].copy()
    if df.empty:
        return None
    for col in stats_mandatory:
        _prepare_numeric(df, col)
    df_long = df.melt(
        id_vars=["full_name"],
        value_vars=stats_mandatory,
        var_name="Stat",
        value_name="Value",
    ).dropna(subset=["Value"])
    if df_long.empty:
        return None
    fig = px.bar(
        df_long,
        x="Stat",
        y="Value",
        color="full_name",
        barmode="group",
        title="Side-by-Side Player Comparison",
        labels=LABELS,
    )
    fig.update_layout(title_x=0.5)
    return fig


def plot_comparison_radar(player_stats, selected_players):
    """
    Radar chart comparing up to 5 players on:
      goals_per_appearance, knockout_goals, cards_per_appearance,
      penalty_conversion, total_awards, subbed_on_goals.
    """
    if not _check_required_cols(player_stats, ["full_name"]):
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
        "subbed_on_goals",
    ]
    if not _check_required_cols(df_radar, needed_cols):
        return None
    for col in needed_cols:
        _prepare_numeric(df_radar, col)
    df_radar[needed_cols] = df_radar[needed_cols].fillna(0)

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
        "Subbed-On",
    ]
    fig = go.Figure()
    for _, row in df_radar.iterrows():
        values = [
            row["goals_per_appearance"],
            row["knockout_scaled"],
            row["discipline_score"],
            row["penalty_conversion"],
            row["awards_scaled"],
            row["subbed_on_scaled"],
        ]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name=row["full_name"],
            )
        )
    fig.update_layout(
        title="Player Comparison Radar",
        title_x=0.5,
        polar={"radialaxis": {"visible": True}},
        showlegend=True,
    )
    return fig


def plot_top_clutch_scorers(player_stats, top_n=5):
    """Horizontal bar chart of top 'n' clutch scorers (goals in 75+ minute)."""
    if not _check_required_cols(player_stats, ["full_name", "clutch_goals"]):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "clutch_goals")
    top_df = _get_top_n(df, "clutch_goals", top_n)
    if top_df is None or top_df.empty:
        return None
    fig = px.bar(
        top_df,
        x="clutch_goals",
        y="full_name",
        orientation="h",
        text="clutch_goals",
        color="full_name",
        title=f"Top {top_n} Clutch Scorers (75+ min)",
        labels=LABELS,

    )
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Clutch Goals",
        yaxis_title="Player Name",
        plot_bgcolor="#e5ecf6",
        paper_bgcolor="#e5ecf6",
        showlegend=False)
    fig.update_traces(textposition="inside")
    return fig


def plot_top_impact_players(player_stats, top_n=5):
    """Horizontal bar chart of top 'n' players who scored after being subbed on."""
    if not _check_required_cols(player_stats, ["full_name", "subbed_on_goals"]):
        return None
    df = player_stats.copy()
    _prepare_numeric(df, "subbed_on_goals")
    top_df = _get_top_n(df, "subbed_on_goals", top_n)
    if top_df is None or top_df.empty:
        return None
    fig = px.bar(
        top_df,
        x="subbed_on_goals",
        y="full_name",
        orientation="h",
        text="subbed_on_goals",
        color="full_name",
        title=f"Top {top_n} Impact Players (Subbed-on Goals)",
        labels=LABELS,
    )
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Goals After Sub",
        yaxis_title="Player Name",
        plot_bgcolor="#e5ecf6",
        paper_bgcolor="#e5ecf6",
        showlegend=False)
    fig.update_traces(textposition="inside")
    return fig
