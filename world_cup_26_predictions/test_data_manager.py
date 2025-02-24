import unittest
import os
import pandas as pd
import numpy as np


from data_manager import (
    load_data,
    create_advanced_player_stats,
    filter_by_gender
)

class TestDataManager(unittest.TestCase):
    """Unit tests for data_manager.py"""

    def test_load_data(self):
        """
        Tests that load_data returns a dictionary of DataFrames
        with the expected keys (filenames minus .csv).
        NOTE: This test expects you to have CSV files in the default 'data/' folder.
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
        # Mock up minimal DataFrames
        players_df = pd.DataFrame({
            "player_id": [1, 2],
            "given_name": ["not applicable", "Alex"],
            "family_name": ["Morgan", "not applicable"],
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
            "match_id": [101, 103, 103]
        })

        matches_df = pd.DataFrame({
            "match_id": [101, 102, 103],
            "knockout_stage": [False, True, True]
        })

        bookings_df = pd.DataFrame({
            "player_id": [2, 2],
            "booking_id": [201, 202]
        })

        substitutions_df = pd.DataFrame({
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

        # Put them all in a dict to simulate loaded CSVs
        dfs_mock = {
            "players": players_df,
            "player_appearances": player_appearances_df,
            "goals": goals_df,
            "matches": matches_df,
            "bookings": bookings_df,
            "substitutions": substitutions_df,
            "penalty_kicks": penalty_kicks_df,
            "award_winners": award_winners_df
        }

        # Call create_advanced_player_stats
        player_stats = create_advanced_player_stats(dfs_mock)

        # Check that player_stats is a DataFrame
        self.assertIsInstance(player_stats, pd.DataFrame)

        # Check that all required columns exist
        expected_columns = [
            "player_id", "full_name", "female",
            "goal_keeper", "defender", "midfielder", "forward",
            "total_appearances", "total_goals", "knockout_goals",
            "goals_per_appearance", "total_cards", "cards_per_appearance",
            "penalty_attempts", "penalty_converted", "penalty_conversion",
            "total_awards", "times_subbed_on", "times_subbed_off"
        ]
        for col in expected_columns:
            self.assertIn(col, player_stats.columns, f"Missing expected column: {col}")

        # Check that name fix has occurred:
        # Player 1 => given_name=not applicable, family_name=Morgan => "Morgan" after fix => "Morgan" not empty? Actually it should become "Morgan" or "Unknown Morgan" depending on logic
        # In our logic, "not applicable" is removed => becomes "", so full_name => "Morgan"
        # Then if the entire name was empty, we'd label it "Unknown"
        # Player 2 => "Alex" "not applicable" => "Alex"
        # Let's see what ended up in the final data:
        p1_name = player_stats.loc[player_stats['player_id'] == 1, 'full_name'].values[0]
        p2_name = player_stats.loc[player_stats['player_id'] == 2, 'full_name'].values[0]

        # Player 1 had "not applicable" + "Morgan" => "Morgan"
        # Player 2 had "Alex" + "not applicable" => "Alex"
        self.assertTrue(
            p1_name == "Morgan" or p1_name == "Unknown Morgan",
            f"Name for player 1 was expected to be 'Morgan' or 'Unknown Morgan', got '{p1_name}'."
        )
        self.assertTrue(
            p2_name == "Alex" or p2_name == "Alex Unknown",
            f"Name for player 2 was expected to be 'Alex' or 'Alex Unknown', got '{p2_name}'."
        )

        # Check the numeric columns for correct calculations
        # Player 1 => total_appearances=2, total_goals=1 (one match_id=101)
        # knockout_goals=0 if match_id=101 was not knockout
        # Actually match 101 has knockout_stage=False => so 0 knockout goals for player 1
        p1_stats = player_stats[player_stats["player_id"] == 1].iloc[0]
        self.assertEqual(p1_stats["total_appearances"], 2)
        self.assertEqual(p1_stats["total_goals"], 1)
        self.assertEqual(p1_stats["knockout_goals"], 0)
        self.assertEqual(p1_stats["goals_per_appearance"], 0.5)

        # Player 2 => total_appearances=1, total_goals=2
        # match_id=103 is knockout => so 2 knockout goals
        p2_stats = player_stats[player_stats["player_id"] == 2].iloc[0]
        self.assertEqual(p2_stats["total_appearances"], 1)
        self.assertEqual(p2_stats["total_goals"], 2)
        self.assertEqual(p2_stats["knockout_goals"], 2)

        # Bookings => Player 2 has 2 bookings => total_cards=2 => cards_per_appearance=2/1=2
        self.assertEqual(p2_stats["total_cards"], 2)
        self.assertEqual(p2_stats["cards_per_appearance"], 2.0)

        # Penalties => Player 1 had 1 attempt (converted=1), Player 2 had 2 attempts (converted=1)
        # => p2 penalty_conversion= 1/2=0.5
        self.assertEqual(p1_stats["penalty_attempts"], 1)
        self.assertEqual(p1_stats["penalty_converted"], 1)
        self.assertEqual(p1_stats["penalty_conversion"], 1.0)

        self.assertEqual(p2_stats["penalty_attempts"], 2)
        self.assertEqual(p2_stats["penalty_converted"], 1)
        self.assertAlmostEqual(p2_stats["penalty_conversion"], 0.5, places=3)

        # Awards => Player 1 has 2 awards, Player 2 has 1
        self.assertEqual(p1_stats["total_awards"], 2)
        self.assertEqual(p2_stats["total_awards"], 1)

        # Substitutions => times_subbed_on => Player 1=1, Player 2=0
        # times_subbed_off => Player 1=0, Player 2=1
        self.assertEqual(p1_stats["times_subbed_on"], 1)
        self.assertEqual(p1_stats["times_subbed_off"], 0)
        self.assertEqual(p2_stats["times_subbed_on"], 0)
        self.assertEqual(p2_stats["times_subbed_off"], 1)

    def test_filter_by_gender(self):
        """
        Tests that filter_by_gender returns the correct subsets.
        """
        # Create a small DataFrame
        df = pd.DataFrame({
            "player_id": [1, 2, 3],
            "full_name": ["Player1", "Player2", "Player3"],
            "female": [True, False, True]
        })

        # all => should return all 3
        df_all = filter_by_gender(df, gender="all")
        self.assertEqual(len(df_all), 3)

        # male => only where female == False => 1
        df_male = filter_by_gender(df, gender="male")
        self.assertEqual(len(df_male), 1)
        self.assertEqual(df_male.iloc[0]["player_id"], 2)

        # female => only where female == True => 2
        df_female = filter_by_gender(df, gender="female")
        self.assertEqual(len(df_female), 2)
        self.assertTrue(all(df_female["female"] == True))

        # unrecognized => returns empty
        df_empty = filter_by_gender(df, gender="unknown")
        self.assertEqual(len(df_empty), 0)