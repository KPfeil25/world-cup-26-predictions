'''
NAME:
    data_manager - Module for loading and preprocessing soccer match data for predictive modeling

DESCRIPTION:
    This module handles the data pipeline for the World Cup 2026 predictions model.
    It includes functions for loading various data files (match results, FIFA rankings,
    temperature data, player information, and awards), creating features from these
    datasets, and preparing the final training dataset with relevant features.

FUNCTIONS:
    load_files - Loads all necessary CSV data files
    feature_addition_rankings - Adds FIFA ranking features to match data
    feature_addition_temperature - Adds temperature features to match data
    feature_addition_players - Adds player-related features to match data
    feature_addition_awards - Adds team award count features to match data
    prepare_training_data - Combines all data sources and prepares the final training dataset

File:
    /tmp/world_cup_26_predictions/predictions/data_manager.py
'''

import os
import pandas as pd

def load_files():
    '''
    Loads all necessary data files from the data directory.
    
    Reads match results, FIFA rankings (men's and women's), temperature data,
    award winners, and player appearances from CSV files.
    
    Returns:
        tuple: Six pandas DataFrames containing:
            - matches: Historical match data
            - mens_rankings: FIFA men's team rankings
            - womens_rankings: FIFA women's team rankings
            - temperature: Temperature data for match locations
            - awards: Award winner information
            - players: Player appearance data
    
    TODO: Add Error Checks
    '''
    path_matches = os.path.join(os.pardir, 'data', 'matches.csv')
    path_mens_rankings = os.path.join(os.pardir, 'data', 'fifa_mens_rankings.csv')
    path_womens_rankings = os.path.join(os.pardir, 'data', 'fifa_womens_rankings.csv')
    path_temps = os.path.join(os.pardir, 'data', 'temperatures_partitioned.csv')
    path_awards = os.path.join(os.pardir, 'data', 'award_winners.csv')
    path_players = os.path.join(os.pardir, 'data', 'player_appearances.csv')
    matches = pd.read_csv(path_matches)
    mens_rankings = pd.read_csv(path_mens_rankings)
    womens_rankings = pd.read_csv(path_womens_rankings)
    temperature = pd.read_csv(path_temps)
    awards = pd.read_csv(path_awards)
    players = pd.read_csv(path_players)
    return matches, mens_rankings, womens_rankings, temperature, awards, players

def feature_addition_rankings(df, rankings):
    '''
    Adds FIFA ranking features to the match data.
    
    Merges match data with FIFA rankings to add home and away team ranks.
    
    Args:
        df (pandas.DataFrame): Match data
        rankings (pandas.DataFrame): FIFA rankings data with 'team' and 'rank' columns
    
    Returns:
        pandas.DataFrame: Match data augmented with 'home_team_rank' and 'away_team_rank' columns
    '''
    home_team = pd.merge(df, rankings, left_on='home_team_name', right_on='team')
    home_team = home_team.rename(columns={'rank': 'home_team_rank'}).drop(columns=['team'])
    full_data = home_team.merge(rankings,
                               left_on='away_team_name',
                               right_on='team')
    full_data = full_data.rename(columns={'rank': 'away_team_rank'}).drop(columns=['team'])
    return full_data

def feature_addition_temperature(df, temperature):
    '''
    Adds temperature features to the match data.
    
    Extracts year from match date and merges with temperature data by year and city.
    
    Args:
        df (pandas.DataFrame): Match data
        temperature (pandas.DataFrame): Temperature data with 'year', 'city_name', 
                                        and 'avg_temp' columns
    
    Returns:
        pandas.DataFrame: Match data augmented with temperature information
    '''
    df['year'] = pd.to_datetime(df['match_date']).dt.year
    df = pd.merge(df, temperature, left_on=['year', 'city_name'], right_on=['year', 'city_name'])
    df.drop(columns=['type'], inplace=True)
    return df

def feature_addition_players(df, players):
    '''
    Adds player-related features to the match data.
    
    Merges match data with player appearance data to add home and away player IDs.
    
    Args:
        df (pandas.DataFrame): Match data
        players (pandas.DataFrame): Player appearance data
    
    Returns:
        pandas.DataFrame: Match data augmented with 'home_player_id' and 'away_player_id' columns
    '''
    home_players = pd.merge(df, players, left_on=['match_id', 'home_team_name'],
                            right_on=['match_id', 'team_name'])
    home_players = home_players.rename(columns={'player_id': 'home_player_id'}).drop(
                                columns=['team_name'])
    full_data = home_players.merge(players,
                               left_on=['match_id', 'away_team_name', 'position_code'],
                               right_on=['match_id', 'team_name', 'position_code'])
    full_data = full_data.rename(columns={'player_id': 'away_player_id'}).drop(
                                columns=['team_name'])
    return full_data

def feature_addition_awards(df, awards):
    '''
    Adds team award count features to the match data.
    
    Calculates the number of awards won by each team and adds these counts to the match data.
    
    Args:
        df (pandas.DataFrame): Match data with 'home_team_id' and 'away_team_id' columns
        awards (pandas.DataFrame): Award data with 'team_id' column
    
    Returns:
        pandas.DataFrame: Match data augmented with 'home_team_award_count' 
                          and 'away_team_award_count' columns
    '''
    team_award_counts = {}
    for _, row in awards.iterrows():
        team_id = row['team_id']
        if team_id in team_award_counts:
            team_award_counts[team_id] += 1
        else:
            team_award_counts[team_id] = 1

    def get_team_award_count(team_id):
        if pd.isna(team_id):
            return 0
        return team_award_counts.get(team_id, 0)
    df['home_team_award_count'] = df['home_team_id'].apply(get_team_award_count)
    df['away_team_award_count'] = df['away_team_id'].apply(get_team_award_count)
    return df

def prepare_training_data():
    '''
    Prepares the complete training dataset by combining all data sources.
    
    Loads all data files, separates men's and women's matches, adds relevant features
    from rankings, temperatures, player information, and awards data, and then combines
    everything into a cleaned training dataset with selected columns.
    
    Returns:
        pandas.DataFrame: Final cleaned training data with the following columns:
            - stage_name: Tournament stage
            - stadium_id: Stadium identifier
            - city_name: Host city name
            - home_team_name: Name of home team
            - away_team_name: Name of away team
            - extra_time: Whether extra time was played
            - penalty_shootout: Whether a penalty shootout was held
            - result: Match result
            - home_player_id: Player ID for home team
            - position_code: Position code
            - away_player_id: Player ID for away team
            - home_team_award_count: Number of awards won by home team
            - away_team_award_count: Number of awards won by away team
            - avg_temp: Average temperature
            - year: Year of the match
            - home_team_rank: Mean Fifa ranking of home team
            - away_team_rank: Mean Fifa ranking of away team
    '''
    matches, mens_rankings, womens_rankings, temperatures, awards, players = load_files()
    mens_matches = matches[matches['tournament_name'].str.contains('Men')]
    mens_matches = feature_addition_rankings(mens_matches,
                                            mens_rankings)
    mens_matches = feature_addition_temperature(mens_matches,
                                                temperatures[temperatures['type'] == 'M'])
    womens_matches = matches[matches['tournament_name'].str.contains(
                    'Women')]
    womens_matches = feature_addition_rankings(womens_matches,
                                               womens_rankings)
    womens_matches = feature_addition_temperature(womens_matches,
                                                  temperatures[temperatures['type'] == 'W'])
    augmented_matches = pd.concat([mens_matches, womens_matches], ignore_index=True)
    aug_matches_players = feature_addition_players(
                            augmented_matches, players)
    training_data = feature_addition_awards(
                            aug_matches_players, awards)
    cleaned_training_data = training_data[['stage_name', 'stadium_id',
                                           'city_name', 'home_team_name',
                            'away_team_name', 'extra_time', 'penalty_shootout',
                            'result', 'home_player_id',
                            'position_code', 'away_player_id',
                            'home_team_award_count', 'away_team_award_count',
                            'avg_temp', 'year', 'home_team_rank', 
                            'away_team_rank']]
    return cleaned_training_data
