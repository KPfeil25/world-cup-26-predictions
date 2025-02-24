import os
import pandas as pd
import numpy as np

def load_data(data_path="data"):
    """
    Loads all CSV files from the specified folder into a dictionary of DataFrames.
    Returns a dictionary keyed by CSV filename (minus extension).
    """
    filenames = [
        "award_winners.csv", "host_countries.csv", "players.csv", "substitutions.csv",
        "awards.csv", "manager_appearances.csv", "qualified_teams.csv", "team_appearances.csv",
        "bookings.csv", "manager_appointments.csv", "referee_appearances.csv", "teams.csv",
        "confederations.csv", "managers.csv", "referee_appointments.csv", "tournament_stages.csv",
        "goals.csv", "matches.csv", "referees.csv", "tournament_standings.csv",
        "group_standings.csv", "penalty_kicks.csv", "squads.csv", "tournaments.csv",
        "groups.csv", "player_appearances.csv", "stadiums.csv"
    ]
    
    dfs = {}
    for file in filenames:
        name = os.path.splitext(file)[0]
        dfs[name] = pd.read_csv(os.path.join(data_path, file))
    
    return dfs


def create_advanced_player_stats(dfs):
    """
    Creates an advanced 'player_stats' DataFrame containing metrics such as:
    - Total goals, knockout goals
    - Appearances, goals per appearance
    - Card counts, penalty conversion rates
    - Awards count, substitution patterns
    Also fixes missing/invalid first/last names by using 'Unknown' to avoid empty strings.
    """

    # Extract relevant DataFrames
    players_df = dfs['players'].copy()
    appearances_df = dfs['player_appearances'].copy()
    goals_df = dfs['goals'].copy()
    bookings_df = dfs['bookings'].copy()
    substitutions_df = dfs['substitutions'].copy()
    penalty_kicks_df = dfs['penalty_kicks'].copy()
    award_winners_df = dfs['award_winners'].copy()
    matches_df = dfs['matches'].copy()
    
    # Helper function to clean individual name fields
    def fix_name(name_value):
        """
        Cleans up a name field, replacing 'not applicable', 'n/a', 'na', or NaN with ''.
        Strips leading/trailing whitespace. This ensures partial placeholders are removed.
        """
        if pd.isnull(name_value):
            return ''
        name_str = str(name_value).strip().lower()
        if name_str in ('not applicable', 'n/a', 'na'):
            return ''
        return str(name_value).strip()

    # Apply fix_name to handle missing or "not applicable" values
    players_df['given_name'] = players_df['given_name'].fillna('').apply(fix_name)
    players_df['family_name'] = players_df['family_name'].fillna('').apply(fix_name)

    # Build the full_name column
    players_df['full_name'] = (players_df['given_name'] + ' ' + players_df['family_name']).str.strip()
    # If the entire name is empty, label it as 'Unknown'
    players_df.loc[players_df['full_name'] == '', 'full_name'] = 'Unknown'

    # Merge with matches to identify knockout goals
    goals_merged = goals_df.merge(
        matches_df[['match_id', 'knockout_stage']],
        on='match_id', how='left'
    )

    # Start building the player_stats DataFrame
    player_stats = players_df[[
        'player_id','full_name','female',
        'goal_keeper','defender','midfielder','forward'
    ]].copy()

    # --- Total appearances ---
    appearances_count = (
        appearances_df.groupby('player_id').size()
        .reset_index(name='total_appearances')
    )
    player_stats = player_stats.merge(appearances_count, on='player_id', how='left')
    player_stats['total_appearances'] = player_stats['total_appearances'].fillna(0)

    # --- Total goals ---
    total_goals = (
        goals_df.groupby('player_id').size()
        .reset_index(name='total_goals')
    )
    player_stats = player_stats.merge(total_goals, on='player_id', how='left')
    player_stats['total_goals'] = player_stats['total_goals'].fillna(0)

    # --- Knockout goals ---
    knockout_goals = (
        goals_merged[goals_merged['knockout_stage'] == True]
        .groupby('player_id').size()
        .reset_index(name='knockout_goals')
    )
    player_stats = player_stats.merge(knockout_goals, on='player_id', how='left')
    player_stats['knockout_goals'] = player_stats['knockout_goals'].fillna(0)

    # --- Goals per appearance ---
    player_stats['goals_per_appearance'] = (
        player_stats['total_goals'] / player_stats['total_appearances']
    ).replace([np.inf, np.nan], 0)

    # --- Cards (bookings) ---
    total_cards = (
        bookings_df.groupby('player_id').size()
        .reset_index(name='total_cards')
    )
    player_stats = player_stats.merge(total_cards, on='player_id', how='left')
    player_stats['total_cards'] = player_stats['total_cards'].fillna(0)
    player_stats['cards_per_appearance'] = (
        player_stats['total_cards'] / player_stats['total_appearances']
    ).replace([np.inf, np.nan], 0)

    # --- Penalty conversion ---
    penalty_agg = (
        penalty_kicks_df.groupby('player_id')
        .agg(
            penalty_attempts=('player_id','count'),
            penalty_converted=('converted','sum')
        )
        .reset_index()
    )
    penalty_agg['penalty_conversion'] = (
        penalty_agg['penalty_converted'] / penalty_agg['penalty_attempts']
    ).replace([np.inf, np.nan], 0)

    player_stats = player_stats.merge(penalty_agg, on='player_id', how='left')
    for col in ['penalty_attempts','penalty_converted','penalty_conversion']:
        player_stats[col] = player_stats[col].fillna(0)

    # --- Awards count ---
    awards_count = (
        award_winners_df.groupby('player_id').size()
        .reset_index(name='total_awards')
    )
    player_stats = player_stats.merge(awards_count, on='player_id', how='left')
    player_stats['total_awards'] = player_stats['total_awards'].fillna(0)

    # --- Substitution patterns ---
    sub_on = (
        substitutions_df[substitutions_df['coming_on'] == True]
        .groupby('player_id').size().reset_index(name='times_subbed_on')
    )
    sub_off = (
        substitutions_df[substitutions_df['going_off'] == True]
        .groupby('player_id').size().reset_index(name='times_subbed_off')
    )
    player_stats = player_stats.merge(sub_on, on='player_id', how='left')
    player_stats = player_stats.merge(sub_off, on='player_id', how='left')
    player_stats['times_subbed_on'] = player_stats['times_subbed_on'].fillna(0)
    player_stats['times_subbed_off'] = player_stats['times_subbed_off'].fillna(0)

    return player_stats


def filter_by_gender(player_stats, gender="all"):
    """
    Returns a subset of the player_stats DataFrame based on the gender selection:
    - 'male' for female == False
    - 'female' for female == True
    - 'all' returns the unfiltered dataset
    If no rows match, returns an empty DataFrame.
    """
    if gender == "all":
        return player_stats
    elif gender == "male":
        return player_stats[player_stats['female'] == False]
    elif gender == "female":
        return player_stats[player_stats['female'] == True]
    else:
        # Unrecognized input, return empty
        return player_stats.iloc[0:0]  # empty df