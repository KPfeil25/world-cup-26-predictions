'''
Tests for predictions_app
'''
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
import predictions.predictions_app as app

class TestPredictionsApp(unittest.TestCase):
    """
    Test cases for the World Cup 2026 predictions application
    """
    def setUp(self):
        """
        Set up test fixtures before each test
        """
        self.sample_matches = pd.DataFrame({
            'match_id': [1, 2, 3, 4],
            'tournament_name': ['FIFA World Cup Men', 'FIFA World Cup Men', 
                               'FIFA World Cup Women', 'FIFA World Cup Women'],
            'home_team_name': ['Brazil', 'France', 'USA', 'Germany'],
            'away_team_name': ['Germany', 'Argentina', 'Japan', 'England'],
            'stadium_id': [101, 102, 103, 104],
            'stadium_name': ['Stadium A', 'Stadium B', 'Stadium C', 'Stadium D'],
            'city_name': ['City A', 'City B', 'City C', 'City D'],
            'match_date': ['2018-06-15', '2018-06-16', '2019-06-17', '2019-06-18'],
            'year': [2018, 2018, 2019, 2019]
        })
        self.sample_players = pd.DataFrame({
            'match_id': [1, 1, 2, 2, 3, 3],
            'tournament_name': ['FIFA World Cup Men', 'FIFA World Cup Men',
                               'FIFA World Cup Men', 'FIFA World Cup Men',
                               'FIFA World Cup Women', 'FIFA World Cup Women'],
            'team_name': ['Brazil', 'Germany', 'France', 'Argentina', 'USA', 'Japan'],
            'player_id': [1001, 1002, 1003, 1004, 1005, 1006],
            'player_name': ['Neymar', 'Müller', 'Mbappé', 'Messi', 'Rapinoe', 'Iwabuchi'],
            'position_code': ['FW', 'MF', 'FW', 'FW', 'FW', 'FW'],
            'year': [2018, 2018, 2018, 2018, 2019, 2019]
        })
        self.sample_rankings = pd.DataFrame({
            'team': ['Brazil', 'France', 'Germany', 'Argentina', 'USA', 'Japan'],
            'rank': [1, 2, 3, 4, 1, 5]
        })
        self.sample_awards = pd.DataFrame({
            'tournament_name': ['FIFA World Cup Men', 'FIFA World Cup Men', 'FIFA World Cup Women'],
            'team_name': ['Brazil', 'Brazil', 'USA'],
            'award_name': ['Golden Ball', 'Golden Boot', 'Golden Ball']
        })
        # Mock model and label encoder
        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = np.array([1])
        self.mock_model.predict_proba.return_value = np.array([[0.2, 0.7, 0.1]])
        self.mock_le = MagicMock()
        self.mock_le.inverse_transform.return_value = np.array(['win'])
        # Create sample data dictionary
        self.data_dict = {
            'matches': self.sample_matches,
            'players': self.sample_players,
            'mens_rankings': self.sample_rankings,
            'womens_rankings': self.sample_rankings,
            'awards': self.sample_awards,
            'model': self.mock_model,
            'le': self.mock_le
        }

    def test_get_stadiums_mapping(self):
        """
        Test the stadium mapping function
        """
        stadium_map = app.get_stadiums_mapping(self.sample_matches)
        self.assertEqual(len(stadium_map), 4)
        self.assertEqual(stadium_map[101], 'Stadium A')
        self.assertEqual(stadium_map[104], 'Stadium D')
        test_df = self.sample_matches.copy()
        test_df = test_df.drop('stadium_name', axis=1)
        stadium_map = app.get_stadiums_mapping(test_df)
        self.assertEqual(stadium_map[101], 'Stadium 101')
        empty_df = pd.DataFrame()
        stadium_map = app.get_stadiums_mapping(empty_df)
        self.assertEqual(stadium_map, {})

    def test_get_available_years(self):
        """
        Test retrieving available years for a team
        """
        years = app.get_available_years('Brazil', 'Men', self.sample_matches)
        self.assertIn(2026, years)
        self.assertIn(2018, years)
        self.assertEqual(len(years), 2)
        years = app.get_available_years('Spain', 'Men', self.sample_matches)
        self.assertEqual(len(years), 1)
        self.assertEqual(years[0], 2026)

    def test_get_team_award_count(self):
        """
        Test counting team awards
        """
        count = app.get_team_award_count('Brazil', self.sample_awards)
        self.assertEqual(count, 2)
        count = app.get_team_award_count('France', self.sample_awards)
        self.assertEqual(count, 0)
        count = app.get_team_award_count('Brazil', pd.DataFrame())
        self.assertEqual(count, 0)

    def test_get_team_players(self):
        """
        Test retrieving player roster for a team
        """
        players = app.get_team_players('Brazil', 'Men', 2018, self.sample_players)
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0], 'Neymar')
        players = app.get_team_players('Brazil', 'Men', 2026, self.sample_players)
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0], 'Neymar')
        players = app.get_team_players('Spain', 'Men', 2018, self.sample_players)
        self.assertEqual(players[0], 'No players found for this team/year')

    def test_get_team_rank(self):
        """
        Test retrieving team rank
        """
        rank = app.get_team_rank('Brazil', self.sample_rankings)
        self.assertEqual(rank, 1)
        rank = app.get_team_rank('Spain', self.sample_rankings, default_rank=20)
        self.assertEqual(rank, 20)

    def test_get_city_name(self):
        """
        Test retrieving city name for a stadium
        """
        city = app.get_city_name(101, self.sample_matches)
        self.assertEqual(city, 'City A')
        city = app.get_city_name(999, self.sample_matches, default_name='Unknown City')
        self.assertEqual(city, 'Unknown City')

    def test_extract_team_data(self):
        """
        Test extracting team data for predictions
        """
        rank, awards = app.extract_team_data('Brazil', 'Men', self.data_dict)
        self.assertEqual(rank, 1)
        self.assertEqual(awards, 2)
        rank, awards = app.extract_team_data('USA', 'Women', self.data_dict)
        self.assertEqual(rank, 1)
        self.assertEqual(awards, 1)

    def test_create_match_data(self):
        """
        Test creating match data for prediction
        """
        match_info = {
            'home_team': 'Brazil',
            'away_team': 'Germany',
            'stadium_id': 101,
            'temperature': 25,
            'gender': 'Men'
        }
        match_data = app.create_match_data(match_info, self.data_dict)
        self.assertEqual(match_data['home_team_name'].iloc[0], 'Brazil')
        self.assertEqual(match_data['away_team_name'].iloc[0], 'Germany')
        self.assertEqual(match_data['home_team_rank'].iloc[0], 1)
        self.assertEqual(match_data['away_team_rank'].iloc[0], 3)
        self.assertEqual(match_data['home_team_award_count'].iloc[0], 2)
        self.assertEqual(match_data['away_team_award_count'].iloc[0], 0)

    def test_calculate_confidence(self):
        """
        Test calculating prediction confidence
        """
        match_data = pd.DataFrame({'test': [1]})
        confidence = app.calculate_confidence(self.mock_model, match_data)
        self.assertEqual(confidence, 70.0)
        model_without_proba = MagicMock()
        model_without_proba.predict.return_value = np.array([1])
        del model_without_proba.predict_proba
        confidence = app.calculate_confidence(model_without_proba, match_data,
                                              default_confidence=60)
        self.assertEqual(confidence, 60)

    def test_predict_match(self):
        """
        Test match outcome prediction
        """
        match_info = {
            'home_team': 'Brazil',
            'away_team': 'Germany',
            'stadium_id': 101,
            'temperature': 25,
            'gender': 'Men'
        }
        result, confidence = app.predict_match(match_info, self.data_dict)
        self.assertEqual(result, 'win')
        self.assertEqual(confidence, 70.0)
        self.mock_model.predict.assert_called_once()
        self.mock_le.inverse_transform.assert_called_once()

    def test_get_country_code(self):
        """
        Test converting team name to country code
        """
        self.assertEqual(app.get_country_code('Brazil'), 'br')
        self.assertEqual(app.get_country_code('United States'), 'us')
        self.assertIsNone(app.get_country_code('Unknown Country'))

    def test_prepare_visualization_data(self):
        """
        Test preparation of visualization data
        """
        # Test home team win scenario
        match_result = {
            'home_team': 'Brazil',
            'away_team': 'Germany',
            'home_year': 2018,
            'away_year': 2018,
            'result': 'win',
            'confidence': 80.0
        }
        result_df = app.prepare_visualization_data(match_result)
        self.assertEqual(len(result_df), 4)
        home_win_prob = result_df[(result_df['Team'] == 'Brazil (2018)') &
                                 (result_df['Outcome'] == 'Win Probability')]['Probability'].iloc[0]
        self.assertEqual(home_win_prob, 80.0)
        match_result['result'] = 'loss'
        result_df = app.prepare_visualization_data(match_result)
        away_win_prob = result_df[(result_df['Team'] == 'Germany (2018)') &
                                 (result_df['Outcome'] == 'Win Probability')]['Probability'].iloc[0]
        self.assertEqual(away_win_prob, 80.0)
        match_result['result'] = 'draw'
        result_df = app.prepare_visualization_data(match_result)
        draw_prob = result_df[(result_df['Team'] == 'Brazil (2018)') &
                             (result_df['Outcome'] == 'Draw Probability')]['Probability'].iloc[0]
        self.assertEqual(draw_prob, 80.0)

    def test_get_filtered_teams(self):
        """
        Test filtering teams by gender
        """
        men_teams = app.get_filtered_teams(self.sample_matches, 'Men')
        self.assertEqual(len(men_teams), 2)
        self.assertIn('Brazil', men_teams)
        self.assertIn('France', men_teams)
        women_teams = app.get_filtered_teams(self.sample_matches, 'Women')
        self.assertEqual(len(women_teams), 2)
        self.assertIn('USA', women_teams)
        self.assertIn('Germany', women_teams)

    def test_prepare_stadium_options(self):
        """
        Test preparation of stadium selection options
        """
        stadium_map = {101: 'Maracanã', 102: 'Camp Nou'}
        stadium_options, stadium_display = app.prepare_stadium_options(
            self.sample_matches, stadium_map)
        self.assertEqual(len(stadium_options), 4)
        self.assertEqual(len(stadium_display), 4)
        self.assertIn(101, stadium_options)
        self.assertTrue(any('Maracanã' in display for display in stadium_display))
        self.assertTrue(any('Stadium 103' in display for display in stadium_display))

    def test_get_players_by_year(self):
        """
        Test helper function for retrieving players by year
        """
        with patch('predictions.predictions_app._get_players_by_year') as mock_get_players:
            # Set up the mock's return values for different test cases
            def side_effect(players_df, team, year):
                if team == 'Brazil' and year == 2026:
                    return ['Neymar']
                if team == 'France' and year == 2018:
                    return ['Mbappé']
                if team == 'Spain':
                    return ['No players found for this team/year']
                if isinstance(players_df, pd.DataFrame) and players_df.empty:
                    return ['No team_name column in player data']
                return []
            mock_get_players.side_effect = side_effect
            players = app.get_team_players('Brazil', 'Men', 2026, self.sample_players)
            self.assertEqual(len(players), 1)
            self.assertEqual(players[0], 'Neymar')
            players = app.get_team_players('France', 'Men', 2018, self.sample_players)
            self.assertEqual(len(players), 1)
            self.assertEqual(players[0], 'Mbappé')
            players = app.get_team_players('Spain', 'Men', 2018, self.sample_players)
            self.assertEqual(players[0], 'No players found for this team/year')
            players = app.get_team_players('Brazil', 'Men', 2018, pd.DataFrame())
            self.assertEqual(players[0], 'No team_name column in player data')
            mock_get_players.assert_called()

    def test_display_outcome(self):
        """
        Test outcome display function (mock test)
        """
        # This is a mock test since the function uses streamlit
        with unittest.mock.patch('streamlit.success') as mock_success, \
             unittest.mock.patch('streamlit.error') as mock_error, \
             unittest.mock.patch('streamlit.info') as mock_info:
            app.display_outcome('Brazil', 'Germany', 'win')
            mock_success.assert_called_once()
            mock_error.assert_not_called()
            mock_info.assert_not_called()
            mock_success.reset_mock()
            app.display_outcome('Brazil', 'Germany', 'away team win')
            mock_success.assert_not_called()
            mock_error.assert_called_once()
            mock_info.assert_not_called()
            mock_error.reset_mock()
            app.display_outcome('Brazil', 'Germany', 'draw')
            mock_success.assert_not_called()
            mock_error.assert_not_called()
            mock_info.assert_called_once()

    def test_create_match_data_edge_cases(self):
        """
        Test match data creation with edge cases
        """
        # Missing team in rankings
        match_info = {
            'home_team': 'Unknown Team',
            'away_team': 'Germany',
            'stadium_id': 101,
            'temperature': 25,
            'gender': 'Men'
        }
        match_data = app.create_match_data(match_info, self.data_dict)
        self.assertEqual(match_data['home_team_name'].iloc[0], 'Unknown Team')
        self.assertEqual(match_data['home_team_rank'].iloc[0], 50)
        match_info = {
            'home_team': 'Brazil',
            'away_team': 'Germany',
            'stadium_id': 999,
            'temperature': 25,
            'gender': 'Men'
        }
        match_data = app.create_match_data(match_info, self.data_dict)
        self.assertEqual(match_data['stadium_id'].iloc[0], 999)
        self.assertEqual(match_data['city_name'].iloc[0], 'Unknown')

    def test_calculate_confidence_with_proba(self):
        """
        Test confidence calculation with probability values
        """
        # Create a model that returns actual probability values
        model = MagicMock()
        model.predict_proba.return_value = np.array([[0.15, 0.75, 0.1]])
        match_data = pd.DataFrame({'test': [1]})
        confidence = app.calculate_confidence(model, match_data)
        self.assertEqual(confidence, 75.0)  # highest probability * 100

if __name__ == '__main__':
    unittest.main()
