'''
NAME:
    test_data_manager_ml.py - Unit tests for the data_manager_ml module

DESCRIPTION:
    This module contains unit tests for the data management functionality used in
    the soccer match prediction system. It tests the data loading, feature engineering,
    and data preparation processes, ensuring that all functions properly handle
    various input scenarios including edge cases with missing values.

CLASSES:
    TestDataManagerML - Test suite for data_manager_ml functions

FILE:
    /tmp/world_cup_26_predictions/tests/test_data_manager_ml.py
'''
import os
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from predictions.data_manager_ml import (
    load_files, feature_addition_rankings, feature_addition_temperature,
    feature_addition_players, feature_addition_awards, prepare_training_data
)

class TestDataManagerML(unittest.TestCase):
    '''
    ADD
    '''
    def setUp(self):
        """
        ADD
        """
        # Create sample dataframes for testing
        self.sample_matches = pd.DataFrame({
            'tournament_name': ['Men World Cup', 'Women World Cup'],
            'match_date': ['2022-11-20', '2023-07-20'],
            'home_team_name': ['Team A', 'Team C'],
            'away_team_name': ['Team B', 'Team D'],
            'home_team_id': [1, 3],
            'away_team_id': [2, 4],
            'stadium_id': [101, 102],
            'city_name': ['City1', 'City2']
        })
        self.sample_mens_rankings = pd.DataFrame({
            'team': ['Team A', 'Team B'],
            'rank': [5, 10]
        })
        self.sample_womens_rankings = pd.DataFrame({
            'team': ['Team C', 'Team D'],
            'rank': [3, 8]
        })
        self.sample_temperature = pd.DataFrame({
            'year': [2022, 2023],
            'city_name': ['City1', 'City2'],
            'avg_temp': [25.0, 28.0],
            'type': ['M', 'W']
        })
        self.sample_awards = pd.DataFrame({
            'team_id': [1, 1, 2, 3],
            'award_name': ['Best Team', 'Fair Play', 'Rising Star', 'Top Scorer']
        })
        self.sample_players = pd.DataFrame({
            'match_id': [1, 1, 2, 2],
            'team_name': ['Team A', 'Team B', 'Team C', 'Team D'],
            'player_id': [101, 102, 103, 104],
            'position_code': ['GK', 'GK', 'GK', 'GK']
        })

    @patch('os.path.join')
    @patch('pandas.read_csv')
    def test_load_files(self, mock_read_csv, mock_path_join):
        """Test load_files function"""
        # Setup mock returns
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        mock_read_csv.side_effect = [
            self.sample_matches,
            self.sample_mens_rankings,
            self.sample_womens_rankings,
            self.sample_temperature,
            self.sample_awards,
            self.sample_players
        ]
        # Call function
        matches, mens_rankings, womens_rankings, temperature, awards, players = load_files()
        # Assert results
        self.assertEqual(mock_read_csv.call_count, 6)
        self.assertEqual(len(matches), 2)
        self.assertEqual(len(mens_rankings), 2)
        self.assertEqual(len(womens_rankings), 2)
        self.assertEqual(len(temperature), 2)
        self.assertEqual(len(awards), 4)
        self.assertEqual(len(players), 4)
        # Check paths were constructed correctly
        expected_paths = [
            os.path.join(os.pardir, 'data', 'matches.csv'),
            os.path.join(os.pardir, 'data', 'fifa_mens_rankings.csv'),
            os.path.join(os.pardir, 'data', 'fifa_womens_rankings.csv'),
            os.path.join(os.pardir, 'data', 'temperatures_partitioned.csv'),
            os.path.join(os.pardir, 'data', 'award_winners.csv'),
            os.path.join(os.pardir, 'data', 'player_appearances.csv')
        ]
        for i, expected_path in enumerate(expected_paths):
            self.assertEqual(mock_read_csv.call_args_list[i][0][0], expected_path)

    def test_feature_addition_rankings(self):
        """Test feature_addition_rankings function"""
        df = self.sample_matches.iloc[:1]  # Just take the men's match
        rankings = self.sample_mens_rankings
        result = feature_addition_rankings(df, rankings)
        # Assertions
        self.assertIn('home_team_rank', result.columns)
        self.assertIn('away_team_rank', result.columns)
        self.assertEqual(result['home_team_rank'].iloc[0], 5)
        self.assertEqual(result['away_team_rank'].iloc[0], 10)
        self.assertEqual(len(result), 1)

    def test_feature_addition_temperature(self):
        """Test feature_addition_temperature function"""
        df = pd.DataFrame({
            'match_date': ['2022-11-20'],
            'city_name': ['City1']
        })
        temperature = self.sample_temperature
        result = feature_addition_temperature(df, temperature)
        # Assertions
        self.assertIn('year', result.columns)
        self.assertIn('avg_temp', result.columns)
        self.assertEqual(result['year'].iloc[0], 2022)
        self.assertEqual(result['avg_temp'].iloc[0], 25.0)

    def test_feature_addition_players(self):
        """Test feature_addition_players function"""
        df = pd.DataFrame({
            'match_id': [1],
            'home_team_name': ['Team A'],
            'away_team_name': ['Team B']
        })
        players = pd.DataFrame({
            'match_id': [1, 1],
            'team_name': ['Team A', 'Team B'],
            'player_id': [101, 102],
            'position_code': ['GK', 'GK']
        })
        result = feature_addition_players(df, players)
        # Assertions
        self.assertIn('home_player_id', result.columns)
        self.assertIn('away_player_id', result.columns)
        self.assertEqual(result['home_player_id'].iloc[0], 101)
        self.assertEqual(result['away_player_id'].iloc[0], 102)

    def test_feature_addition_awards(self):
        """Test feature_addition_awards function"""
        df = pd.DataFrame({
            'home_team_id': [1],
            'away_team_id': [2]
        })
        awards = self.sample_awards
        result = feature_addition_awards(df, awards)
        # Assertions
        self.assertIn('home_team_award_count', result.columns)
        self.assertIn('away_team_award_count', result.columns)
        self.assertEqual(result['home_team_award_count'].iloc[0], 2)# Team 1 has 2 awards
        self.assertEqual(result['away_team_award_count'].iloc[0], 1)# Team 2 has 1 award

    def test_feature_addition_awards_with_nan(self):
        """Test feature_addition_awards with NaN values"""
        df = pd.DataFrame({
            'home_team_id': [1],
            'away_team_id': [np.nan]
        })
        awards = self.sample_awards
        result = feature_addition_awards(df, awards)
        # Assertions
        self.assertEqual(result['home_team_award_count'].iloc[0], 2)
        self.assertEqual(result['away_team_award_count'].iloc[0], 0)  # NaN teams have 0 awards

    @patch('predictions.data_manager_ml.load_files')
    def test_prepare_training_data(self, mock_load_files):
        """Test prepare_training_data function"""
        # Setup mock data
        matches = pd.DataFrame({
            'tournament_name': ['Men World Cup', 'Women World Cup'],
            'match_date': ['2022-11-20', '2023-07-20'],
            'home_team_name': ['Team A', 'Team C'],
            'away_team_name': ['Team B', 'Team D'],
            'home_team_id': [1, 3],
            'away_team_id': [2, 4],
            'stadium_id': [101, 102],
            'city_name': ['City1', 'City2'],
            'extra_time': [False, True],
            'penalty_shootout': [False, False],
            'result': ['win', 'draw'],
            'stage_name': ['Group stage', 'Group stage']
        })
        mock_load_files.return_value = (
            matches,
            self.sample_mens_rankings,
            self.sample_womens_rankings,
            self.sample_temperature,
            self.sample_awards,
            self.sample_players
        )
        # Mock the feature addition functions
        with patch('predictions.data_manager_ml.feature_addition_rankings',
                   return_value=matches.copy()), \
             patch('predictions.data_manager_ml.feature_addition_temperature',
                   return_value=matches.copy()), \
             patch('predictions.data_manager_ml.feature_addition_players',
                   return_value=matches.copy()), \
             patch('predictions.data_manager_ml.feature_addition_awards',
                   return_value=matches.assign(
                 home_team_award_count=2,
                 away_team_award_count=1,
                 home_player_id=101,
                 away_player_id=102,
                 position_code='GK',
                 avg_temp=25.0,
                 year=2022,
                 home_team_rank=5,
                 away_team_rank=10
             )):
            # Call function
            result = prepare_training_data()
            # Assertions
            self.assertIn('home_team_rank', result.columns)
            self.assertIn('away_team_rank', result.columns)
            self.assertIn('home_team_award_count', result.columns)
            self.assertIn('away_team_award_count', result.columns)
            self.assertIn('avg_temp', result.columns)
            self.assertEqual(len(result.columns), 17)  # Check all expected columns are present

if __name__ == '__main__':
    unittest.main()
