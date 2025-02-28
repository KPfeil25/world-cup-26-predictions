import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio

# Use a more colorful Plotly template
pio.templates.default = "plotly"

#color sequence
DEFAULT_COLOR_SEQ = px.colors.qualitative.Bold


def plot_top_scorers(player_stats, n=10, color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of top scorers by total_goals."""
    if player_stats.empty:
        return None

    df_top = player_stats.nlargest(n, 'total_goals').copy()
    fig = px.bar(
        df_top,
        x='full_name',
        y='total_goals',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} All-Time Scorers"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Total Goals")
    return fig


def plot_top_knockout_scorers(player_stats, n=10, color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of top scorers by knockout_goals."""
    if player_stats.empty:
        return None

    df_top = player_stats.nlargest(n, 'knockout_goals').copy()
    fig = px.bar(
        df_top,
        x='full_name',
        y='knockout_goals',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Knockout-Stage Scorers"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Knockout Goals")
    return fig


def plot_goals_per_appearance(player_stats, min_appearances=10, n=10,
                              color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of top players by goals_per_appearance (>= min_appearances)."""
    df_eligible = player_stats[player_stats['total_appearances'] >= min_appearances]
    if df_eligible.empty:
        return None

    df_top = df_eligible.nlargest(n, 'goals_per_appearance').copy()
    fig = px.bar(
        df_top,
        x='full_name',
        y='goals_per_appearance',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Goals/App (Min {min_appearances} Apps)"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Goals/App")
    return fig


def plot_most_awarded_players(player_stats, n=10, color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of top players by total_awards."""
    df_top = player_stats.nlargest(n, 'total_awards').copy()
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x='full_name',
        y='total_awards',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Most Awarded Players"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Awards")
    return fig


def plot_best_penalty_conversion(player_stats, min_attempts=1, n=10,
                                 color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of top players by penalty_conversion (>= min_attempts)."""
    df_eligible = player_stats[player_stats['penalty_attempts'] >= min_attempts]
    if df_eligible.empty:
        return None

    df_top = df_eligible.nlargest(n, 'penalty_conversion').copy()
    fig = px.bar(
        df_top,
        x='full_name',
        y='penalty_conversion',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Penalty Conversion (Min {min_attempts} Attempts)"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Conversion Rate")
    return fig


def plot_highest_card_rate(player_stats, min_appearances=10, n=10,
                           color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of players with highest cards_per_appearance (>= min_appearances)."""
    df_eligible = player_stats[player_stats['total_appearances'] >= min_appearances]
    if df_eligible.empty:
        return None

    df_top = df_eligible.nlargest(n, 'cards_per_appearance').copy()
    fig = px.bar(
        df_top,
        x='full_name',
        y='cards_per_appearance',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Cards/App (Min {min_appearances} Apps)"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="Cards/App")
    return fig


def plot_substitution_patterns(player_stats, n=10, color_by=None, hover_cols=None, color_seq=None):
    """
    Returns two figures (fig_on, fig_off):
      - top 'n' players by times_subbed_on
      - top 'n' players by times_subbed_off
    """
    if player_stats.empty:
        return None, None

    df_on = player_stats.nlargest(n, 'times_subbed_on').copy()
    fig_on = px.bar(
        df_on,
        x='full_name',
        y='times_subbed_on',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} - Times Subbed On"
    )
    fig_on.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="# Subbed On")

    df_off = player_stats.nlargest(n, 'times_subbed_off').copy()
    fig_off = px.bar(
        df_off,
        x='full_name',
        y='times_subbed_off',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} - Times Subbed Off"
    )
    fig_off.update_layout(title_x=0.5, xaxis_title="Player", yaxis_title="# Subbed Off")

    return fig_on, fig_off


def plot_position_appearances(player_stats, position_bool_column='goal_keeper',
                              position_label='Goalkeepers',
                              n=10,
                              color_by=None, hover_cols=None, color_seq=None):
    """Bar chart of top 'n' players in a particular position by total_appearances."""
    df_pos = player_stats[player_stats[position_bool_column] == True]
    if df_pos.empty:
        return None

    df_top = df_pos.nlargest(n, 'total_appearances').copy()
    fig = px.bar(
        df_top,
        x='full_name',
        y='total_appearances',
        color=color_by,
        hover_data=hover_cols,
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} {position_label} by Appearances"
    )
    fig.update_layout(title_x=0.5, xaxis_title=position_label, yaxis_title="Appearances")
    return fig


def compare_players(player_stats, selected_players):
    """
    Returns a DataFrame comparing the selected players on key stats,
    sorted by total_goals desc.
    """
    if player_stats.empty or not selected_players:
        return pd.DataFrame()

    subset = player_stats[player_stats['full_name'].isin(selected_players)]
    if subset.empty:
        return pd.DataFrame()

    subset = subset.sort_values('total_goals', ascending=False)
    columns_to_show = [
        'player_id','full_name','continent',
        'total_appearances','total_goals','knockout_goals','goals_per_appearance',
        'total_cards','cards_per_appearance',
        'penalty_attempts','penalty_converted','penalty_conversion',
        'total_awards','times_subbed_on','times_subbed_off',
        'subbed_on_goals','clutch_goals'
    ]
    subset = subset[columns_to_show].reset_index(drop=True)
    return subset


def plot_compare_players_side_by_side(player_stats, selected_players):
    """
    Creates a grouped bar chart to compare multiple players across several key metrics side-by-side.
    """
    df = player_stats[player_stats['full_name'].isin(selected_players)].copy()
    if df.empty:
        return None

    df = df.sort_values('total_goals', ascending=False)

    stats_of_interest = {
        'total_goals': 'Total Goals',
        'knockout_goals': 'Knockout Goals',
        'total_appearances': 'Appearances',
        'penalty_conversion': 'Penalty Conv.',
        'total_awards': 'Awards'
    }

    records = []
    for _, row in df.iterrows():
        for stat_col, stat_label in stats_of_interest.items():
            records.append({
                'Player': row['full_name'],
                'Statistic': stat_label,
                'Value': row[stat_col]
            })
    long_df = pd.DataFrame(records)

    fig = px.bar(
        long_df,
        x='Statistic',
        y='Value',
        color='Player',
        barmode='group',
        title="Player Comparison (Side-by-Side)",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(title_x=0.5, xaxis_title="", yaxis_title="Value")
    return fig


def plot_comparison_radar(player_stats, selected_players):
    """
    Radar chart comparing up to 5 players on 6 advanced metrics:
      - goals_per_appearance
      - knockout_goals (scaled log)
      - discipline_score (1/(1+cards_per_appearance))
      - penalty_conversion
      - total_awards (scaled log)
      - subbed_on_goals (scaled log)
    """
    df = player_stats[player_stats['full_name'].isin(selected_players)].copy()
    if df.empty:
        return None

    # Limit to 5
    df = df.head(5)

    df['knockout_scaled'] = np.log1p(df['knockout_goals']) * 5
    df['discipline_score'] = 1 / (1 + df['cards_per_appearance'])
    df['awards_scaled'] = np.log1p(df['total_awards']) * 5
    df['subbed_on_scaled'] = np.log1p(df['subbed_on_goals']) * 5

    categories = [
        "goals_per_appearance",
        "knockout_scaled",
        "discipline_score",
        "penalty_conversion",
        "awards_scaled",
        "subbed_on_scaled"
    ]
    labels = ["Goals/App", "Knockout", "Discipline", "Pen. Conv.", "Awards", "Subbed-On"]

    fig = go.Figure()
    for _, row in df.iterrows():
        values = [
            row["goals_per_appearance"],
            row["knockout_scaled"],
            row["discipline_score"],
            row["penalty_conversion"],
            row["awards_scaled"],
            row["subbed_on_scaled"]
        ]
        fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', name=row['full_name']))

    fig.update_layout(
        title="Player Comparison Radar",
        title_x=0.5,
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True
    )
    return fig


def plot_top_clutch_scorers(player_stats, n=5, color_seq=None):
    """
    Horizontal bar chart of the top 'n' clutch scorers (goals in 75+ minute).
    """
    if player_stats.empty or 'clutch_goals' not in player_stats.columns:
        return None

    df_top = player_stats.nlargest(n, 'clutch_goals').copy()
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x='clutch_goals',
        y='full_name',
        orientation='h',
        text='clutch_goals',
        color='full_name',
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Clutch Scorers (75+ min)"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Clutch Goals", yaxis_title="Player", showlegend=False)
    fig.update_traces(textposition='inside')
    return fig


def plot_top_impact_players(player_stats, n=5, color_seq=None):
    """
    Horizontal bar chart of the top 'n' impact players 
    (goals scored after being subbed on).
    """
    if player_stats.empty or 'subbed_on_goals' not in player_stats.columns:
        return None

    df_top = player_stats.nlargest(n, 'subbed_on_goals').copy()
    if df_top.empty:
        return None

    fig = px.bar(
        df_top,
        x='subbed_on_goals',
        y='full_name',
        orientation='h',
        text='subbed_on_goals',
        color='full_name',
        color_discrete_sequence=color_seq or DEFAULT_COLOR_SEQ,
        title=f"Top {n} Impact Players (Subbed-on Goals)"
    )
    fig.update_layout(title_x=0.5, xaxis_title="Goals After Sub", yaxis_title="Player", showlegend=False)
    fig.update_traces(textposition='inside')
    return fig