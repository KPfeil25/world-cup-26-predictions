"""
Data management module for loading and transforming player statistics from
CSV files related to World Cup data.
"""

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
        A dictionary with keys as filenames (minus .csv extension) and
        values as DataFrames.
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
    for file_name in filenames:
        name = os.path.splitext(file_name)[0]
        full_path = os.path.join(data_path, file_name)
        if os.path.exists(full_path):
            dfs[name] = pd.read_csv(full_path)
        else:
            # If file doesn't exist, create an empty DF with no columns
            dfs[name] = pd.DataFrame()

    return dfs


def _fix_name(raw_name):
    """
    Cleans up a raw name value by lowercasing, trimming, and handling
    not-applicable values.
    """
    if pd.isnull(raw_name):
        return ""
    val = str(raw_name).strip().lower()
    if val in ("not applicable", "n/a", "na"):
        return ""
    return str(raw_name).strip()


def _prepare_player_base(players_df):
    """
    Creates the initial 'player_stats' DataFrame with core columns like full_name, birth_date, etc.
    """
    # Ensure 'given_name' and 'family_name' columns exist before fillna/apply:
    if "given_name" not in players_df.columns:
        players_df["given_name"] = ""
    else:
        players_df["given_name"] = players_df["given_name"].fillna("").apply(_fix_name)

    if "family_name" not in players_df.columns:
        players_df["family_name"] = ""
    else:
        players_df["family_name"] = players_df["family_name"].fillna("").apply(_fix_name)

    players_df["full_name"] = (
        players_df["given_name"] + " " + players_df["family_name"]
        ).str.strip()
    players_df.loc[players_df["full_name"] == "", "full_name"] = "Unknown"

    # Parse birth_date (optional)
    if "birth_date" in players_df.columns:
        players_df["birth_date"] = pd.to_datetime(players_df["birth_date"], errors="coerce")
        players_df["birth_year"] = players_df["birth_date"].dt.year
    else:
        players_df["birth_date"] = pd.NaT
        players_df["birth_year"] = np.nan

    base_cols = [
        "player_id",
        "full_name",
        "female",
        "goal_keeper",
        "defender",
        "midfielder",
        "forward",
        "birth_date",
        "birth_year",
    ]
    # Ensure those columns exist
    for col in base_cols:
        if col not in players_df.columns:
            players_df[col] = np.nan

    return players_df[base_cols].copy()


def _merge_appearances(appearances_df, player_stats):
    """
    Merges total appearances into player_stats.
    """
    if not appearances_df.empty and "player_id" in appearances_df.columns:
        appearances_count = (
            appearances_df.groupby("player_id").size().reset_index(name="total_appearances")
        )
    else:
        appearances_count = pd.DataFrame({"player_id": [], "total_appearances": []})

    merged = player_stats.merge(appearances_count, on="player_id", how="left")
    merged["total_appearances"] = merged["total_appearances"].fillna(0)
    return merged


def _merge_goals(goals_df, player_stats):
    """
    Merges total goals into player_stats.
    """
    if not goals_df.empty and "player_id" in goals_df.columns:
        total_goals = goals_df.groupby("player_id").size().reset_index(name="total_goals")
    else:
        total_goals = pd.DataFrame({"player_id": [], "total_goals": []})

    merged = player_stats.merge(total_goals, on="player_id", how="left")
    merged["total_goals"] = merged["total_goals"].fillna(0)
    return merged


def _merge_knockout_goals(matches_df, goals_df, player_stats):
    """
    Merges knockout goals if 'knockout_stage' == True in matches.
    """
    if (not matches_df.empty
            and "knockout_stage" in matches_df.columns
            and not goals_df.empty
            and "player_id" in goals_df.columns):
        goals_merged = goals_df.merge(
            matches_df[["match_id", "knockout_stage"]],
            on="match_id",
            how="left"
        )
        knockout_goals = goals_merged[goals_merged["knockout_stage"].eq(True)]
        knockout_agg = (
            knockout_goals.groupby("player_id").size().reset_index(name="knockout_goals")
        )
    else:
        knockout_agg = pd.DataFrame({"player_id": [], "knockout_goals": []})

    merged = player_stats.merge(knockout_agg, on="player_id", how="left")
    merged["knockout_goals"] = merged["knockout_goals"].fillna(0)
    return merged


def _add_goals_per_appearance(player_stats):
    """
    Adds goals_per_appearance column to player_stats.
    """
    merged = player_stats.copy()
    merged["goals_per_appearance"] = (
        merged["total_goals"] / merged["total_appearances"]
    ).replace([np.inf, np.nan], 0)
    return merged


def _merge_cards(bookings_df, player_stats):
    """
    Merges booking info => total_cards => cards_per_appearance.
    """
    if not bookings_df.empty and "player_id" in bookings_df.columns:
        total_cards = (
            bookings_df.groupby("player_id").size().reset_index(name="total_cards")
        )
    else:
        total_cards = pd.DataFrame({"player_id": [], "total_cards": []})

    merged = player_stats.merge(total_cards, on="player_id", how="left")
    merged["total_cards"] = merged["total_cards"].fillna(0)
    merged["cards_per_appearance"] = (
        merged["total_cards"] / merged["total_appearances"]
    ).replace([np.inf, np.nan], 0)
    return merged


def _merge_penalties(penalty_kicks_df, player_stats):
    """
    Merges penalty attempt/conversion data => penalty_attempts,
    penalty_converted, penalty_conversion.
    """
    if not penalty_kicks_df.empty and "player_id" in penalty_kicks_df.columns:
        pen_agg = (
            penalty_kicks_df.groupby("player_id")
            .agg(
                penalty_attempts=("player_id", "count"),
                penalty_converted=("converted", "sum")
            )
            .reset_index()
        )
        pen_agg["penalty_conversion"] = (
            pen_agg["penalty_converted"] / pen_agg["penalty_attempts"]
        ).replace([np.inf, np.nan], 0)
    else:
        pen_agg = pd.DataFrame({
            "player_id": [],
            "penalty_attempts": [],
            "penalty_converted": [],
            "penalty_conversion": []
        })

    merged = player_stats.merge(pen_agg, on="player_id", how="left")
    for col in ["penalty_attempts", "penalty_converted", "penalty_conversion"]:
        merged[col] = merged[col].fillna(0)
    return merged


def _merge_awards(award_winners_df, player_stats):
    """
    Merges award counts => total_awards.
    """
    if not award_winners_df.empty and "player_id" in award_winners_df.columns:
        awards_count = (
            award_winners_df.groupby("player_id").size().reset_index(name="total_awards")
        )
    else:
        awards_count = pd.DataFrame({"player_id": [], "total_awards": []})

    merged = player_stats.merge(awards_count, on="player_id", how="left")
    merged["total_awards"] = merged["total_awards"].fillna(0)
    return merged


def _merge_substitutions(substitutions_df, goals_df, player_stats):
    """
    Merges times subbed on/off + subbed-on goals.
    """
    merged = player_stats.copy()

    # Merge sub_on / sub_off
    if not substitutions_df.empty:
        # Provide default series of False if "coming_on"/"going_off" are missing
        sub_on = substitutions_df[
            substitutions_df.get("coming_on",
            pd.Series(False, index=substitutions_df.index)).eq(True)
        ]
        sub_off = substitutions_df[
            substitutions_df.get("going_off",
            pd.Series(False, index=substitutions_df.index)).eq(True)
        ]
        sub_on_count = sub_on.groupby("player_id").size().reset_index(name="times_subbed_on")
        sub_off_count = sub_off.groupby("player_id").size().reset_index(name="times_subbed_off")
    else:
        sub_on_count = pd.DataFrame({"player_id": [], "times_subbed_on": []})
        sub_off_count = pd.DataFrame({"player_id": [], "times_subbed_off": []})

    merged = merged.merge(sub_on_count, on="player_id", how="left")
    merged = merged.merge(sub_off_count, on="player_id", how="left")
    merged["times_subbed_on"] = merged["times_subbed_on"].fillna(0)
    merged["times_subbed_off"] = merged["times_subbed_off"].fillna(0)

    # Merge subbed_on_goals only if both match_id/player_id columns exist in goals_df
    has_needed_cols = (
        not goals_df.empty
        and not substitutions_df.empty
        and {"match_id", "player_id"}.issubset(goals_df.columns)
        and {"match_id", "player_id"}.issubset(sub_on.columns)
    )
    if has_needed_cols:
        goals_merge_sub = goals_df.merge(
            sub_on[["match_id", "player_id"]],
            on=["match_id", "player_id"],
            how="inner"
        )
        subbed_on_goals_count = (
            goals_merge_sub.groupby("player_id").size().reset_index(name="subbed_on_goals")
        )
    else:
        subbed_on_goals_count = pd.DataFrame({"player_id": [], "subbed_on_goals": []})

    merged = merged.merge(subbed_on_goals_count, on="player_id", how="left")
    merged["subbed_on_goals"] = merged["subbed_on_goals"].fillna(0)

    return merged


def _merge_clutch_goals(goals_df, matches_df, player_stats):
    """
    Merges 'clutch_goals' (75+ min) into player_stats.
    """
    merged = player_stats.copy()
    if (not goals_df.empty
            and "minute_regulation" in goals_df.columns
            and not matches_df.empty):
        # If needed, also merges knockout_stage from matches
        if "knockout_stage" in matches_df.columns:
            goals_merged = goals_df.merge(
                matches_df[["match_id", "knockout_stage"]],
                on="match_id",
                how="left"
            )
        else:
            goals_merged = goals_df.copy()

        goals_merged["goal_minute"] = goals_merged["minute_regulation"].fillna(0)
        clutch_df = goals_merged[goals_merged["goal_minute"] >= 75]
        clutch_count = clutch_df.groupby("player_id").size().reset_index(name="clutch_goals")
    else:
        clutch_count = pd.DataFrame({"player_id": [], "clutch_goals": []})

    merged = merged.merge(clutch_count, on="player_id", how="left")
    merged["clutch_goals"] = merged["clutch_goals"].fillna(0)
    return merged


def _merge_primary_team(squads_df, teams_df, player_stats):
    """
    Merges the primary team/confederation/continent into player_stats.
    """
    merged = player_stats.copy()
    if not squads_df.empty and not teams_df.empty:
        needed_in_squads = ["team_id", "player_id"]
        for col in needed_in_squads:
            if col not in squads_df.columns:
                squads_df[col] = np.nan

        needed_in_teams = ["team_id", "confederation_code"]
        for col in needed_in_teams:
            if col not in teams_df.columns:
                teams_df[col] = np.nan

        squads_teams = squads_df.drop(
            columns=["team_name", "team_code"], errors="ignore"
        ).merge(
            teams_df[["team_id", "team_name", "team_code", "confederation_code", "region_name"]],
            on="team_id",
            how="left"
        )

        # Identify primary team for each player
        team_count = squads_teams.groupby(
            ["player_id", "team_id", "team_name", "team_code"]
        ).size().reset_index(name="count")
        team_count = team_count.sort_values("count", ascending=False)
        primary_team = team_count.drop_duplicates(subset=["player_id"], keep="first").copy()
        primary_team.rename(
            columns={
                "team_name": "primary_team_name",
                "team_code": "primary_team_code"
            },
            inplace=True
        )

        merged = merged.merge(
            primary_team[["player_id", "primary_team_name", "primary_team_code"]],
            on="player_id",
            how="left"
        )
        merged["primary_team_name"] = merged["primary_team_name"].fillna("Unknown")
        merged["primary_team_code"] = merged["primary_team_code"].fillna("---")

        # Identify primary confederation
        squads_teams2 = squads_df.merge(
            teams_df[["team_id", "confederation_code"]],
            on="team_id",
            how="left"
        )
        conf_count = (
            squads_teams2.groupby(["player_id", "confederation_code"])
            .size()
            .reset_index(name="count")
        )
        conf_count = conf_count.sort_values("count", ascending=False)
        primary_conf = conf_count.drop_duplicates(subset=["player_id"], keep="first").copy()
        primary_conf.rename(
            columns={"confederation_code": "primary_confederation_code"},
            inplace=True
        )

        merged = merged.merge(
            primary_conf[["player_id", "primary_confederation_code"]],
            on="player_id",
            how="left"
        )

        confed_to_continent = {
            "UEFA": "Europe",
            "CONMEBOL": "South America",
            "CONCACAF": "North America",
            "AFC": "Asia",
            "CAF": "Africa",
            "OFC": "Oceania"
        }
        merged["continent"] = merged["primary_confederation_code"].map(confed_to_continent)
        merged["continent"] = merged["continent"].fillna("Unknown")
        merged["primary_confederation"] = merged["primary_confederation_code"].fillna("Unknown")
    else:
        merged["primary_team_name"] = "Unknown"
        merged["primary_team_code"] = "---"
        merged["primary_confederation_code"] = np.nan
        merged["continent"] = "Unknown"
        merged["primary_confederation"] = "Unknown"

    return merged


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
    players_df = dfs.get("players", pd.DataFrame()).copy()
    appearances_df = dfs.get("player_appearances", pd.DataFrame()).copy()
    goals_df = dfs.get("goals", pd.DataFrame()).copy()
    bookings_df = dfs.get("bookings", pd.DataFrame()).copy()
    substitutions_df = dfs.get("substitutions", pd.DataFrame()).copy()
    penalty_kicks_df = dfs.get("penalty_kicks", pd.DataFrame()).copy()
    award_winners_df = dfs.get("award_winners", pd.DataFrame()).copy()
    matches_df = dfs.get("matches", pd.DataFrame()).copy()
    squads_df = dfs.get("squads", pd.DataFrame()).copy()
    teams_df = dfs.get("teams", pd.DataFrame()).copy()

    # Build the base stats
    player_stats = _prepare_player_base(players_df)

    # Merge in various metrics
    player_stats = _merge_appearances(appearances_df, player_stats)
    player_stats = _merge_goals(goals_df, player_stats)
    player_stats = _merge_knockout_goals(matches_df, goals_df, player_stats)
    player_stats = _add_goals_per_appearance(player_stats)
    player_stats = _merge_cards(bookings_df, player_stats)
    player_stats = _merge_penalties(penalty_kicks_df, player_stats)
    player_stats = _merge_awards(award_winners_df, player_stats)
    player_stats = _merge_substitutions(substitutions_df, goals_df, player_stats)
    player_stats = _merge_clutch_goals(goals_df, matches_df, player_stats)
    player_stats = _merge_primary_team(squads_df, teams_df, player_stats)

    return player_stats


def filter_players(player_stats, gender="All", continent="All", position="All"):
    """
    Returns a subset of the player_stats DataFrame based on gender, continent, and position filters.
    """
    filtered_stats = player_stats.copy()

    # Gender filter
    if gender == "Men":
        filtered_stats = filtered_stats[filtered_stats["female"].eq(False)]
    elif gender == "Women":
        filtered_stats = filtered_stats[filtered_stats["female"].eq(True)]

    # Continent filter
    if continent != "All":
        filtered_stats = filtered_stats[filtered_stats["continent"] == continent]

    # Position filter
    if position == "Goalkeeper":
        filtered_stats = filtered_stats[filtered_stats["goal_keeper"].eq(True)]
    elif position == "Defender":
        filtered_stats = filtered_stats[filtered_stats["defender"].eq(True)]
    elif position == "Midfielder":
        filtered_stats = filtered_stats[filtered_stats["midfielder"].eq(True)]
    elif position == "Forward":
        filtered_stats = filtered_stats[filtered_stats["forward"].eq(True)]

    return filtered_stats
