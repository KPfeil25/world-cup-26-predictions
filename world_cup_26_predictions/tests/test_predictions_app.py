'''
NAME:
    test_predictions_app - Unit tests for the World Cup match prediction application

DESCRIPTION:
    This module contains unit tests for validating the functionality of the 
    predictions application responsible for predicting World Cup match outcomes.
    The tests cover data processing, utility functions, model prediction logic,
    and Streamlit-based display functions.

CLASSES:
    TestPredictionsApp - Defines a suite of unit tests for functions and methods 
                         within predictions_app.py

FILE:
    /tmp/world_cup_26_predictions/tests/test_predictions_app.py
'''
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
import world_cup_26_predictions.predictions.predictions_app as app

class TestPredictionsApp(unittest.TestCase):
    """
    Unit tests for the World Cup 2026 predictions application module.
    This class validates the correctness of individual functions and workflows inside 
    predictions_app.py, ensuring data processing, prediction logic, and user interface 
    rendering perform as expected.
    """
    def setUp(self):
        """
        Set up common test fixtures.
        Initializes sample data for matches, players, rankings, and awards, and mocks 
        for the model and label encoder to be reused across multiple test cases.
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
        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = np.array([1])
        self.mock_model.predict_proba.return_value = np.array([[0.2, 0.7, 0.1]])
        self.mock_le = MagicMock()
        self.mock_le.inverse_transform.return_value = np.array(['win'])
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
        Test the mapping of stadium IDs to stadium names.
        Verifies that the function correctly creates a mapping dictionary from match data.
        Also tests fallback behavior when 'stadium_name' is missing or when data is empty.
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
        Test retrieval of available years for a specific team.
        Checks that years are returned correctly for teams present in the dataset and 
        fallback logic (e.g., default year) is applied for teams not present.
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
        Test calculation of total awards won by a team.
        Ensures that the correct count of awards is returned for a team, including 
        handling cases with no awards or an empty dataframe.
        """
        count = app.get_team_award_count('Brazil', self.sample_awards)
        self.assertEqual(count, 2)
        count = app.get_team_award_count('France', self.sample_awards)
        self.assertEqual(count, 0)
        count = app.get_team_award_count('Brazil', pd.DataFrame())
        self.assertEqual(count, 0)

    def test_get_team_players(self):
        """
        Test retrieval of player names for a team and year.
        Validates that player rosters are correctly extracted based on gender and year, 
        and that fallback messages are returned for teams with no player data.
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
        Test retrieval of a team's ranking.
        Checks that the correct team rank is returned when available, and that a 
        default rank is used when the team is missing from the rankings data.
        """
        rank = app.get_team_rank('Brazil', self.sample_rankings)
        self.assertEqual(rank, 1)
        rank = app.get_team_rank('Spain', self.sample_rankings, default_rank=20)
        self.assertEqual(rank, 20)

    def test_get_city_name(self):
        """
        Test extraction of city name given a stadium ID.
        Ensures city names are correctly mapped to stadium IDs, with a fallback 
        to a default city name when the stadium is missing.
        """
        city = app.get_city_name(101, self.sample_matches)
        self.assertEqual(city, 'City A')
        city = app.get_city_name(999, self.sample_matches, default_name='Unknown City')
        self.assertEqual(city, 'Unknown City')

    def test_extract_team_data(self):
        """
        Test feature extraction for a team.
        Verifies that rank and award count are correctly returned for a team 
        based on gender and tournament data.
        """
        rank, awards = app.extract_team_data('Brazil', 'Men', self.data_dict)
        self.assertEqual(rank, 1)
        self.assertEqual(awards, 2)
        rank, awards = app.extract_team_data('USA', 'Women', self.data_dict)
        self.assertEqual(rank, 1)
        self.assertEqual(awards, 1)

    def test_create_match_data(self):
        """
        Test the creation of a match feature set for model input.
        Checks that all necessary fields (team names, ranks, awards, etc.) are populated 
        correctly when creating match data for prediction.
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
        Test calculation of prediction confidence score.
        Ensures that the confidence score is computed correctly based on model 
        probability outputs or falls back to a default confidence when 
        predict_proba is unavailable.
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
        Test the full match prediction pipeline.
        Validates that the model returns the correct match outcome and confidence 
        score using mock predictions.
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
        Test conversion of country names to ISO 3166-1 alpha-2 country codes.
        Verifies correct ISO code mapping for known countries and ensures None 
        is returned for unknown or invalid inputs.
        """
        self.assertEqual(app.get_country_code('Brazil'), 'br')
        self.assertEqual(app.get_country_code('United States'), 'us')
        self.assertIsNone(app.get_country_code('Unknown Country'))

    def test_prepare_visualization_data(self):
        """
        Test preparation of data used for post-prediction visualizations.
        Ensures that the output dataframe contains the correct win/loss/draw probabilities 
        mapped to teams based on the match result.
        """
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
        Test filtering teams based on gender.
        Ensures that teams are filtered correctly for men's or women's tournaments 
        based on match data.
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
        Test preparation of stadium selection dropdown options.
        Verifies correct formatting of dropdown options for stadiums, including fallback 
        labels when stadium names are missing.
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
        Test internal helper function for retrieving players by year.
        Uses mock patching to simulate behavior of _get_players_by_year under 
        different scenarios, including missing player data.
        """
        with patch('predictions.predictions_app._get_players_by_year') as mock_get_players:
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
        Test the display of match outcome results in the Streamlit app.
        Verifies correct usage of Streamlit success, error, and info messages 
        depending on match result (home win, away win, draw).
        """
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
        Test match data creation for edge cases.
        Covers scenarios such as missing rankings or invalid stadium IDs to 
        ensure fallback values are applied correctly.
        """
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
        Test confidence score calculation when predict_proba returns actual values.
        Ensures correct confidence extraction based on the highest probability.
        """
        model = MagicMock()
        model.predict_proba.return_value = np.array([[0.15, 0.75, 0.1]])
        match_data = pd.DataFrame({'test': [1]})
        confidence = app.calculate_confidence(model, match_data)
        self.assertEqual(confidence, 75.0)


    def test_predictions_app_functions(self):
        """
        Test multiple high-level functions in predictions_app for integration.

        Includes end-to-end tests for:
        - Player info retrieval
        - Displaying match details, team info, and prediction results in Streamlit
        - Displaying visualizations and charts
        - Handling full prediction flow with Streamlit UI components
        """
        home_player_id, away_player_id, position_code = app.get_player_info(
            'Brazil', 'Germany', self.sample_players
        )
        self.assertEqual(home_player_id, 1001)
        self.assertEqual(away_player_id, 1002)
        self.assertEqual(position_code, 'FW')
        match_info = {
            'home_team': 'Brazil',
            'away_team': 'Germany',
            'stadium_name': 'Stadium A',
            'stadium_id': 101,
            'temperature': 25,
            'home_year': 2018,
            'away_year': 2018,
            'gender': 'Men'
        }
        with patch('streamlit.markdown') as mock_markdown:
            app.display_match_details(match_info, self.data_dict)
            self.assertTrue(mock_markdown.called)
        team_data = {'name': 'Brazil', 'year': 2018, 'gender': 'Men'}
        with patch('streamlit.markdown'), patch('streamlit.image'), patch('streamlit.write'):
            app.display_team_info(team_data, MagicMock(), self.data_dict)
        result_data = {'result': 'win', 'confidence': 75.0}
        with patch('streamlit.markdown'):
            app.display_prediction_results(match_info, result_data, self.data_dict)
        result_df = pd.DataFrame({
            'Team': ['Brazil (2018)', 'Germany (2018)'],
            'Outcome': ['Win Probability', 'Draw Probability'],
            'Probability': [75.0, 25.0]
        })
        with patch('streamlit.altair_chart') as mock_chart:
            app.display_chart(result_df)
            mock_chart.assert_called_once()
        with patch('streamlit.markdown') as mock_markdown:
            app.display_prediction_context()
            self.assertTrue(mock_markdown.called)
        match_settings = {
            'home_team': 'Brazil',
            'away_team': 'Germany',
            'stadium_id': 101,
            'stadium_name': 'Stadium A',
            'temperature': 25,
            'home_year': 2018,
            'away_year': 2018,
            'gender': 'Men'
        }
        with patch('streamlit.button', return_value=True), patch('streamlit.markdown'):
            app.handle_prediction(match_settings, self.data_dict, MagicMock())
        stadium_map = {101: 'Stadium A', 102: 'Stadium B'}
        with patch('streamlit.selectbox', side_effect=['Men', 'Brazil',
                                                       'Germany', 2018, 2018, 0]), \
             patch('streamlit.slider', return_value=25), \
             patch('streamlit.markdown'):
            match_settings = app.configure_match_settings(self.data_dict, stadium_map, MagicMock())
            self.assertEqual(match_settings['home_team'], 'Brazil')
            self.assertEqual(match_settings['away_team'], 'Germany')
            self.assertEqual(match_settings['temperature'], 25)
            self.assertEqual(match_settings['gender'], 'Men')
            self.assertIn('stadium_id', match_settings)
            self.assertIn('stadium_name', match_settings)

if __name__ == '__main__':
    unittest.main()
