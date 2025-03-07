'''
NAME:
    data_manager - This module loads in the data and preprocesses it for our model

File:
    /tmp/world_cup_26_predictions/predictions/data_manager.py
'''

import os
import pandas as pd

def load_files():
    '''
    This function loads all the necessary files
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
    This function creates features based on rankings
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
    This function create features based on temperature
    '''
    df['year'] = pd.to_datetime(df['match_date']).dt.year
    df = pd.merge(df, temperature, left_on=['year', 'city_name'], right_on=['year', 'city_name'])
    df.drop(columns=['type'], inplace=True)
    return df

def feature_addition_players(df, players):
    '''
    This function creates features based on players
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
    This function creates features based on awards
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
    This function prepares training data
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
                            'avg_temp', 'year']]
    return cleaned_training_data
