import unittest
import pandas as pd
import numpy as np

from data_manager import (
    load_data,
    create_advanced_player_stats,
    filter_players
)

class TestDataManager(unittest.TestCase):
    """Unit tests for data_manager.py"""

    def test_load_data(self):
        """
        Tests that load_data returns a dictionary of DataFrames
        with the expected keys (filenames minus .csv).

        NOTE: This test expects you to have CSV files in the default 'data/' folder
        or adjust the data_path accordingly.
        If certain CSV files are missing, they'll just be empty DataFrames.
        """
        dfs = load_data(data_path="data")

        # Check that dfs is a dictionary
        self.assertIsInstance(dfs, dict, "load_data should return a dictionary.")

        # Check a few expected keys are present (spot-check)
        expected_keys = [
            "players", "goals", "matches",
            "player_appearances", "bookings"
        ]
        for key in expected_keys:
            self.assertIn(key, dfs, f"'{key}' should be a key in the returned dictionary.")

        # Check that each item in dfs is a pandas DataFrame
        for key, df in dfs.items():
            self.assertIsInstance(df, pd.DataFrame, f"dfs['{key}'] should be a DataFrame.")

    def test_create_advanced_player_stats(self):
        """
        Tests create_advanced_player_stats with mock DataFrames to ensure
        columns are created properly and name fields are fixed.
        """
        # -- Mock up minimal DataFrames --
        players_df = pd.DataFrame({
            "player_id": [1, 2],
            "given_name": ["not applicable", "Alex"],
            "family_name": ["Morgan", "not applicable"],
            "birth_date": [None, None],
            "female": [True, False],
            "goal_keeper": [False, False],
            "defender": [False, False],
            "midfielder": [False, True],
            "forward": [True, False]
        })

        player_appearances_df = pd.DataFrame({
            "player_id": [1, 1, 2],
            "match_id": [101, 102, 103]
        })

        goals_df = pd.DataFrame({
            "player_id": [1, 2, 2],
            "match_id": [101, 103, 103],
            "minute_regulation": [10, 85, 90]  # Player 2 => two clutch goals
        })

        matches_df = pd.DataFrame({
            "match_id": [101, 102, 103],
            "knockout_stage": [False, True, True]
        })

        bookings_df = pd.DataFrame({
            "player_id": [2, 2],
            "booking_id": [201, 202],
            "match_id": [103, 103]
        })

        # Must have match_id for merges on substitutions
        substitutions_df = pd.DataFrame({
            "match_id": [101, 102],
            "player_id": [1, 2],
            "coming_on": [True, False],
            "going_off": [False, True]
        })

        penalty_kicks_df = pd.DataFrame({
            "player_id": [1, 2, 2],
            "converted": [1, 0, 1]
        })

        award_winners_df = pd.DataFrame({
            "player_id": [1, 1, 2],
            "award_id": [501, 502, 501]
        })

        # -- Add minimal squads & teams so we get primary_confederation_code --
        squads_df = pd.DataFrame({
            "player_id": [1, 2],
            "team_id": [555, 666],
            "team_name": ["USA", "Brazil"],
            "team_code": ["USA", "BRA"]
        })

        teams_df = pd.DataFrame({
            "team_id": [555, 666],
            "team_name": ["USA", "Brazil"],
            "team_code": ["USA", "BRA"],
            "region_name": ["North America", "South America"],
            "confederation_code": ["CONCACAF", "CONMEBOL"]
        })

        # Put them all in a dict to simulate loaded CSVs
        dfs_mock = {
            "players": players_df,
            "player_appearances": player_appearances_df,
            "goals": goals_df,
            "matches": matches_df,
            "bookings": bookings_df,
            "substitutions": substitutions_df,
            "penalty_kicks": penalty_kicks_df,
            "award_winners": award_winners_df,
            "squads": squads_df,
            "teams": teams_df
        }

        # -- Call create_advanced_player_stats --
        player_stats = create_advanced_player_stats(dfs_mock)

        # Check that player_stats is a DataFrame
        self.assertIsInstance(player_stats, pd.DataFrame)

        # Check that all required columns exist
        expected_columns = [
            "player_id", "full_name", "female",
            "goal_keeper", "defender", "midfielder", "forward",
            "birth_date", "birth_year",
            "total_appearances", "total_goals", "knockout_goals",
            "goals_per_appearance", "total_cards", "cards_per_appearance",
            "penalty_attempts", "penalty_converted", "penalty_conversion",
            "total_awards", "times_subbed_on", "times_subbed_off",
            "subbed_on_goals", "clutch_goals",
            "primary_team_name", "primary_team_code",
            "primary_confederation_code", "continent", "primary_confederation"
        ]
        for col in expected_columns:
            self.assertIn(col, player_stats.columns, f"Missing expected column: {col}")

        # -- Check name fix occurred --
        # Player 1 => given_name="not applicable" => "" + family_name="Morgan" => "Morgan"
        # Player 2 => given_name="Alex" + family_name="not applicable" => "Alex"
        p1_name = player_stats.loc[player_stats['player_id'] == 1, 'full_name'].values[0]
        p2_name = player_stats.loc[player_stats['player_id'] == 2, 'full_name'].values[0]

        self.assertTrue(
            p1_name == "Morgan" or p1_name == "Unknown Morgan",
            f"Expected 'Morgan' or 'Unknown Morgan', got '{p1_name}'."
        )
        self.assertTrue(
            p2_name == "Alex" or p2_name == "Alex Unknown",
            f"Expected 'Alex' or 'Alex Unknown', got '{p2_name}'."
        )

        # -- Numeric columns for correct calculations --
        # Player 1 => total_appearances=2, total_goals=1 => match_id=101 => non-knockout
        p1_stats = player_stats[player_stats["player_id"] == 1].iloc[0]
        self.assertEqual(p1_stats["total_appearances"], 2)
        self.assertEqual(p1_stats["total_goals"], 1)
        self.assertEqual(p1_stats["knockout_goals"], 0)
        self.assertEqual(p1_stats["goals_per_appearance"], 0.5)

        # Player 2 => total_appearances=1, total_goals=2 => match_id=103 => knockout => 2 knockout goals
        p2_stats = player_stats[player_stats["player_id"] == 2].iloc[0]
        self.assertEqual(p2_stats["total_appearances"], 1)
        self.assertEqual(p2_stats["total_goals"], 2)
        self.assertEqual(p2_stats["knockout_goals"], 2)

        # Bookings => Player 2 has 2 => total_cards=2 => cards_per_appearance=2/1=2
        self.assertEqual(p2_stats["total_cards"], 2)
        self.assertEqual(p2_stats["cards_per_appearance"], 2.0)

        # Penalties => Player 1 => 1 attempt (converted=1) => conversion=1.0
        #             Player 2 => 2 attempts (converted=1) => conversion=0.5
        self.assertEqual(p1_stats["penalty_attempts"], 1)
        self.assertEqual(p1_stats["penalty_converted"], 1)
        self.assertEqual(p1_stats["penalty_conversion"], 1.0)

        self.assertEqual(p2_stats["penalty_attempts"], 2)
        self.assertEqual(p2_stats["penalty_converted"], 1)
        self.assertAlmostEqual(p2_stats["penalty_conversion"], 0.5, places=3)

        # Awards => Player 1 => 2 awards, Player 2 => 1 award
        self.assertEqual(p1_stats["total_awards"], 2)
        self.assertEqual(p2_stats["total_awards"], 1)

        # Substitutions => times_subbed_on => Player 1=1, Player 2=0
        #                 times_subbed_off => Player 1=0, Player 2=1
        self.assertEqual(p1_stats["times_subbed_on"], 1)
        self.assertEqual(p1_stats["times_subbed_off"], 0)
        self.assertEqual(p2_stats["times_subbed_on"], 0)
        self.assertEqual(p2_stats["times_subbed_off"], 1)

        # Clutch goals => Player 2 => goals in minute 85, 90 => total 2
        self.assertEqual(p1_stats["clutch_goals"], 0)
        self.assertEqual(p2_stats["clutch_goals"], 2)

        # Primary team => (from squads + teams)
        self.assertEqual(p1_stats["primary_team_name"], "USA")
        self.assertEqual(p1_stats["primary_team_code"], "USA")
        self.assertEqual(p1_stats["primary_confederation_code"], "CONCACAF")
        self.assertEqual(p1_stats["continent"], "North America")

        self.assertEqual(p2_stats["primary_team_name"], "Brazil")
        self.assertEqual(p2_stats["primary_team_code"], "BRA")
        self.assertEqual(p2_stats["primary_confederation_code"], "CONMEBOL")
        self.assertEqual(p2_stats["continent"], "South America")

    def test_filter_players_gender(self):
        """
        Tests that filter_players returns the correct subsets by gender.
        """
        df = pd.DataFrame({
            "player_id": [1, 2, 3],
            "female": [True, False, True],
            # Minimal columns just to support filtering
            "goal_keeper": [False, False, False],
            "defender": [False, False, False],
            "midfielder": [False, False, False],
            "forward": [False, False, False],
            "continent": ["Unknown", "Unknown", "Unknown"]
        })

        # No filter => should return all 3
        df_all = filter_players(df, gender="All")
        self.assertEqual(len(df_all), 3, "Should return all rows when gender='All'")

        # "Men" => only where female == False => 1 row
        df_men = filter_players(df, gender="Men")
        self.assertEqual(len(df_men), 1, "Should return only the male row when gender='Men'")
        self.assertEqual(df_men.iloc[0]["player_id"], 2)

        # "Women" => only where female == True => 2 rows
        df_women = filter_players(df, gender="Women")
        self.assertEqual(len(df_women), 2, "Should return only the female rows when gender='Women'")
        self.assertTrue(all(df_women["female"] == True))

    def test_filter_players_continent(self):
        """
        Tests that filter_players returns the correct subsets by continent.
        """
        df = pd.DataFrame({
            "player_id": [1, 2, 3, 4],
            "female": [True, False, True, False],
            "continent": ["Europe", "Asia", "Europe", "North America"],
            "goal_keeper": [False, False, False, False],
            "defender": [False, False, False, False],
            "midfielder": [False, False, False, False],
            "forward": [False, False, False, False]
        })

        # No filter => return all 4
        df_all = filter_players(df)
        self.assertEqual(len(df_all), 4)

        # Filter by "Europe"
        df_europe = filter_players(df, continent="Europe")
        self.assertEqual(len(df_europe), 2)
        self.assertTrue(all(df_europe["continent"] == "Europe"))

        # Filter by "North America"
        df_na = filter_players(df, continent="North America")
        self.assertEqual(len(df_na), 1)
        self.assertTrue(all(df_na["continent"] == "North America"))

        # Filter by "Unknown" => should return none here
        df_unknown = filter_players(df, continent="Unknown")
        self.assertEqual(len(df_unknown), 0)

    def test_filter_players_position(self):
        """
        Tests that filter_players correctly filters by position.
        """
        df = pd.DataFrame({
            "player_id": [1, 2, 3, 4],
            "female": [True, True, False, False],
            "continent": ["Europe", "Asia", "Europe", "Asia"],
            "goal_keeper": [True, False, False, False],
            "defender": [False, True, False, False],
            "midfielder": [False, False, True, False],
            "forward": [False, False, False, True]
        })

        # No filter => all 4
        df_all = filter_players(df)
        self.assertEqual(len(df_all), 4)

        # Goalkeepers => just player_id=1
        df_gk = filter_players(df, position="Goalkeeper")
        self.assertEqual(len(df_gk), 1)
        self.assertTrue(all(df_gk["goal_keeper"] == True))

        # Defender => just player_id=2
        df_def = filter_players(df, position="Defender")
        self.assertEqual(len(df_def), 1)
        self.assertTrue(all(df_def["defender"] == True))

        # Midfielder => player_id=3
        df_mid = filter_players(df, position="Midfielder")
        self.assertEqual(len(df_mid), 1)
        self.assertTrue(all(df_mid["midfielder"] == True))

        # Forward => player_id=4
        df_fwd = filter_players(df, position="Forward")
        self.assertEqual(len(df_fwd), 1)
        self.assertTrue(all(df_fwd["forward"] == True))

if __name__ == "__main__":
    unittest.main()