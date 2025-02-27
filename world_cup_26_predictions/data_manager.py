import os
import pandas as pd
import numpy as np

def load_data(data_path="data"):
    """
    Loads all CSV files from the specified folder into a dictionary of DataFrames.
    Returns a dictionary keyed by CSV filename (minus extension).

    Parameters
    ----------
    data_path : str, optional
        The folder path where CSV files are located, by default "data"

    Returns
    -------
    dict of pd.DataFrame
        A dictionary with keys as filenames (minus .csv extension) and values as DataFrames.
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
        full_path = os.path.join(data_path, file)
        if os.path.exists(full_path):
            dfs[name] = pd.read_csv(full_path)
        else:
            # If file doesn't exist, create an empty DF with no columns
            dfs[name] = pd.DataFrame()

    return dfs


def create_advanced_player_stats(dfs):
    """
    Creates an advanced 'player_stats' DataFrame containing metrics such as:
      - total_goals, knockout_goals
      - appearances, goals_per_appearance
      - card counts, penalty conversion rates
      - awards count, substitution patterns
      - 'clutch' goals (75+ minute), subbed-on goals
      - confederation -> continent mapping
      - primary team (country)
      - birth_date parsing for potential youngest/oldest checks

    Parameters
    ----------
    dfs : dict of pd.DataFrame
        Dictionary of DataFrames keyed by table names, typically from `load_data`.

    Returns
    -------
    pd.DataFrame
        A DataFrame with one row per player, enriched with advanced metrics.
    """
    # Extract relevant DataFrames (some may be empty if they don't exist)
    players_df = dfs['players'].copy()
    appearances_df = dfs['player_appearances'].copy()
    goals_df = dfs['goals'].copy()
    bookings_df = dfs['bookings'].copy()
    substitutions_df = dfs['substitutions'].copy()
    penalty_kicks_df = dfs['penalty_kicks'].copy()
    award_winners_df = dfs['award_winners'].copy()
    matches_df = dfs['matches'].copy()
    squads_df = dfs.get('squads', pd.DataFrame()).copy()
    teams_df = dfs.get('teams', pd.DataFrame()).copy()

    # --- Clean up player names ---
    def _fix_name(x):
        if pd.isnull(x):
            return ''
        val = str(x).strip().lower()
        if val in ('not applicable', 'n/a', 'na'):
            return ''
        return str(x).strip()

    # Fix given_name/family_name
    players_df['given_name'] = players_df['given_name'].fillna('').apply(_fix_name)
    players_df['family_name'] = players_df['family_name'].fillna('').apply(_fix_name)
    players_df['full_name'] = (players_df['given_name'] + ' ' + players_df['family_name']).str.strip()
    players_df.loc[players_df['full_name'] == '', 'full_name'] = 'Unknown'

    # Parse birth_date (optional)
    if 'birth_date' in players_df.columns:
        players_df['birth_date'] = pd.to_datetime(players_df['birth_date'], errors='coerce')
        players_df['birth_year'] = players_df['birth_date'].dt.year
    else:
        players_df['birth_date'] = pd.NaT
        players_df['birth_year'] = np.nan

    # Base player_stats DataFrame
    base_cols = [
        'player_id','full_name','female',
        'goal_keeper','defender','midfielder','forward',
        'birth_date','birth_year'
    ]
    # Fallback if any missing columns in players
    for col in base_cols:
        if col not in players_df.columns:
            players_df[col] = np.nan

    player_stats = players_df[base_cols].copy()

    # --- Appearances ---
    if not appearances_df.empty and 'player_id' in appearances_df.columns:
        appearances_count = appearances_df.groupby('player_id').size().reset_index(name='total_appearances')
    else:
        appearances_count = pd.DataFrame({'player_id': [], 'total_appearances': []})

    player_stats = player_stats.merge(appearances_count, on='player_id', how='left')
    player_stats['total_appearances'] = player_stats['total_appearances'].fillna(0)

    # --- Goals ---
    if not goals_df.empty and 'player_id' in goals_df.columns:
        total_goals = goals_df.groupby('player_id').size().reset_index(name='total_goals')
    else:
        total_goals = pd.DataFrame({'player_id': [], 'total_goals': []})

    player_stats = player_stats.merge(total_goals, on='player_id', how='left')
    player_stats['total_goals'] = player_stats['total_goals'].fillna(0)

    # --- Knockout goals ---
    if not matches_df.empty and 'knockout_stage' in matches_df.columns and 'player_id' in goals_df.columns:
        goals_merged = goals_df.merge(
            matches_df[['match_id','knockout_stage']], 
            on='match_id', 
            how='left'
        )
        knockout_goals = (
            goals_merged[goals_merged['knockout_stage'] == True]
            .groupby('player_id').size().reset_index(name='knockout_goals')
        )
    else:
        # Fallback if no data
        knockout_goals = pd.DataFrame({'player_id': [], 'knockout_goals': []})

    player_stats = player_stats.merge(knockout_goals, on='player_id', how='left')
    player_stats['knockout_goals'] = player_stats['knockout_goals'].fillna(0)

    # --- Goals per appearance ---
    player_stats['goals_per_appearance'] = (
        player_stats['total_goals'] / player_stats['total_appearances']
    ).replace([np.inf, np.nan], 0)

    # --- Cards ---
    if not bookings_df.empty and 'player_id' in bookings_df.columns:
        total_cards = bookings_df.groupby('player_id').size().reset_index(name='total_cards')
    else:
        total_cards = pd.DataFrame({'player_id': [], 'total_cards': []})

    player_stats = player_stats.merge(total_cards, on='player_id', how='left')
    player_stats['total_cards'] = player_stats['total_cards'].fillna(0)
    player_stats['cards_per_appearance'] = (
        player_stats['total_cards'] / player_stats['total_appearances']
    ).replace([np.inf, np.nan], 0)

    # --- Penalty conversion ---
    if not penalty_kicks_df.empty and 'player_id' in penalty_kicks_df.columns:
        pen_agg = (
            penalty_kicks_df
            .groupby('player_id')
            .agg(
                penalty_attempts=('player_id','count'),
                penalty_converted=('converted','sum')
            )
            .reset_index()
        )
        pen_agg['penalty_conversion'] = (
            pen_agg['penalty_converted'] / pen_agg['penalty_attempts']
        ).replace([np.inf, np.nan], 0)
    else:
        pen_agg = pd.DataFrame({
            'player_id': [],
            'penalty_attempts': [],
            'penalty_converted': [],
            'penalty_conversion': []
        })

    player_stats = player_stats.merge(pen_agg, on='player_id', how='left')
    for col in ['penalty_attempts','penalty_converted','penalty_conversion']:
        player_stats[col] = player_stats[col].fillna(0)

    # --- Awards ---
    if not award_winners_df.empty and 'player_id' in award_winners_df.columns:
        awards_count = award_winners_df.groupby('player_id').size().reset_index(name='total_awards')
    else:
        awards_count = pd.DataFrame({'player_id': [], 'total_awards': []})

    player_stats = player_stats.merge(awards_count, on='player_id', how='left')
    player_stats['total_awards'] = player_stats['total_awards'].fillna(0)

    # --- Substitutions (times subbed on/off) ---
    if not substitutions_df.empty:
        # times_subbed_on
        sub_on = (
            substitutions_df[substitutions_df.get('coming_on', False) == True]
            .groupby('player_id').size().reset_index(name='times_subbed_on')
        )
        # times_subbed_off
        sub_off = (
            substitutions_df[substitutions_df.get('going_off', False) == True]
            .groupby('player_id').size().reset_index(name='times_subbed_off')
        )
    else:
        sub_on = pd.DataFrame({'player_id': [], 'times_subbed_on': []})
        sub_off = pd.DataFrame({'player_id': [], 'times_subbed_off': []})

    player_stats = player_stats.merge(sub_on, on='player_id', how='left')
    player_stats = player_stats.merge(sub_off, on='player_id', how='left')
    player_stats['times_subbed_on'] = player_stats['times_subbed_on'].fillna(0)
    player_stats['times_subbed_off'] = player_stats['times_subbed_off'].fillna(0)

    # --- Subbed-on goals (impact goals) ---
    # We'll merge on ['match_id','player_id'] if columns exist
    if (
        not goals_df.empty and 
        not substitutions_df.empty and 
        'match_id' in goals_df.columns and 
        'match_id' in substitutions_df.columns
    ):
        goals_merge_sub = goals_df.merge(
            substitutions_df[substitutions_df['coming_on'] == True],
            on=['match_id','player_id'], suffixes=('_goal','_sub'), how='inner'
        )
        subbed_on_goals_count = (
            goals_merge_sub.groupby('player_id').size().reset_index(name='subbed_on_goals')
        )
    else:
        subbed_on_goals_count = pd.DataFrame({'player_id': [], 'subbed_on_goals': []})

    player_stats = player_stats.merge(subbed_on_goals_count, on='player_id', how='left')
    player_stats['subbed_on_goals'] = player_stats['subbed_on_goals'].fillna(0)

    # --- Clutch goals (75+ minute) ---
    # Only if goals_df + matches_df exist
    if (
        not goals_df.empty and 
        'minute_regulation' in goals_df.columns and 
        not matches_df.empty
    ):
        # Re-use or create a goals_merged
        if 'knockout_stage' in matches_df.columns:
            # Possibly already done above
            goals_merged2 = goals_df.merge(
                matches_df[['match_id','knockout_stage']], 
                on='match_id', how='left'
            )
        else:
            # Fallback if no knockout_stage
            goals_merged2 = goals_df.copy()

        goals_merged2['goal_minute'] = goals_merged2['minute_regulation'].fillna(0)
        clutch_df = goals_merged2[goals_merged2['goal_minute'] >= 75]
        clutch_count = clutch_df.groupby('player_id').size().reset_index(name='clutch_goals')
    else:
        clutch_count = pd.DataFrame({'player_id': [], 'clutch_goals': []})

    player_stats = player_stats.merge(clutch_count, on='player_id', how='left')
    player_stats['clutch_goals'] = player_stats['clutch_goals'].fillna(0)

    # --- Identify player's primary team (country) ---
    if not squads_df.empty and not teams_df.empty:
        # Merge squads and teams to get confederation_code, etc.
        # but first rename columns if missing
        needed_in_squads = ['team_id','player_id']
        for col in needed_in_squads:
            if col not in squads_df.columns:
                squads_df[col] = np.nan

        needed_in_teams = ['team_id','confederation_code']
        for col in needed_in_teams:
            if col not in teams_df.columns:
                teams_df[col] = np.nan

        # We'll do a separate squads->teams merge for the "primary team"
        squads_teams = squads_df.drop(
            columns=['team_name','team_code'], errors='ignore'
        ).merge(
            teams_df[['team_id','team_name','team_code','confederation_code','region_name']],
            on='team_id', how='left'
        )
        # Count how often each player_id + team_id occurs
        team_count = squads_teams.groupby(
            ['player_id','team_id','team_name','team_code']
        ).size().reset_index(name='count')
        team_count = team_count.sort_values('count', ascending=False)
        primary_team = team_count.drop_duplicates(subset=['player_id'], keep='first').copy()
        primary_team.rename(columns={
            'team_name': 'primary_team_name',
            'team_code': 'primary_team_code'
        }, inplace=True)

        player_stats = player_stats.merge(
            primary_team[['player_id','primary_team_name','primary_team_code']],
            on='player_id', how='left'
        )
        player_stats['primary_team_name'] = player_stats['primary_team_name'].fillna('Unknown')
        player_stats['primary_team_code'] = player_stats['primary_team_code'].fillna('---')

        # For confederation->continent
        squads_teams2 = squads_df.merge(
            teams_df[['team_id','confederation_code']], 
            on='team_id', how='left'
        )
        conf_count = squads_teams2.groupby(['player_id','confederation_code']).size().reset_index(name='count')
        conf_count = conf_count.sort_values('count', ascending=False)
        primary_conf = conf_count.drop_duplicates(subset=['player_id'], keep='first').copy()
        primary_conf.rename(columns={'confederation_code': 'primary_confederation_code'}, inplace=True)

        player_stats = player_stats.merge(
            primary_conf[['player_id','primary_confederation_code']],
            on='player_id', how='left'
        )

        confed_to_continent = {
            'UEFA': 'Europe',
            'CONMEBOL': 'South America',
            'CONCACAF': 'North America',
            'AFC': 'Asia',
            'CAF': 'Africa',
            'OFC': 'Oceania'
        }
        player_stats['continent'] = player_stats['primary_confederation_code'].map(confed_to_continent)
        player_stats['continent'] = player_stats['continent'].fillna('Unknown')
        player_stats['primary_confederation'] = player_stats['primary_confederation_code'].fillna('Unknown')
    else:
        # Provide the columns even if squads or teams are empty
        player_stats['primary_team_name'] = 'Unknown'
        player_stats['primary_team_code'] = '---'
        player_stats['primary_confederation_code'] = np.nan
        player_stats['continent'] = 'Unknown'
        player_stats['primary_confederation'] = 'Unknown'

    return player_stats


def filter_players(player_stats, gender="All", continent="All", position="All"):
    """
    Returns a subset of the player_stats DataFrame based on gender, continent, and position filters.

    Parameters
    ----------
    player_stats : pd.DataFrame
        The full player_stats DataFrame, typically from `create_advanced_player_stats`.
    gender : {"All", "Men", "Women"}, optional
        Filter for men's or women's data. "All" applies no gender filter.
    continent : {"All", "Europe", "South America", "North America", "Asia", "Africa", "Oceania", "Unknown"}, optional
        Filter by continent. "All" applies no filter.
    position : {"All", "Goalkeeper", "Defender", "Midfielder", "Forward"}, optional
        Filter by position. "All" applies no position filter.

    Returns
    -------
    pd.DataFrame
        A filtered subset of the player_stats DataFrame.
    """
    df = player_stats.copy()

    # Gender filter
    if gender == "Men":
        df = df[df['female'] == False]
    elif gender == "Women":
        df = df[df['female'] == True]

    # Continent filter
    if continent != "All":
        df = df[df['continent'] == continent]

    # Position filter
    if position == "Goalkeeper":
        df = df[df['goal_keeper'] == True]
    elif position == "Defender":
        df = df[df['defender'] == True]
    elif position == "Midfielder":
        df = df[df['midfielder'] == True]
    elif position == "Forward":
        df = df[df['forward'] == True]

    return df