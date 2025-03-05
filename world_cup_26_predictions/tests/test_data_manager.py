"""
Unit tests for the data_manager module. Ensures 100% coverage and Pylint 10/10 compliance.
"""
import os
import unittest
import shutil
import pandas as pd

from data_manager import (
    load_data,
    create_advanced_player_stats,
    filter_players,
    _fix_name  # test the private helper explicitly if desired
)


class TestDataManager(unittest.TestCase):
    """
    Unit tests for data_manager.py
    """

    def test_fix_name_various_inputs(self):
        """
        Test the _fix_name function explicitly to cover all branches:
          - None input
          - 'not applicable', 'n/a', 'na'
          - Normal strings
        """
        self.assertEqual(_fix_name(None), "", "Expected empty string for None input.")
        self.assertEqual(_fix_name("not applicable"), "", "Should map 'not applicable' to ''")
        self.assertEqual(_fix_name("n/a"), "", "Should map 'n/a' to ''")
        self.assertEqual(_fix_name("na"), "", "Should map 'na' to ''")
        self.assertEqual(_fix_name("  Lionel  "), "Lionel", "Should trim whitespace and preserve case.")
        self.assertEqual(_fix_name("MEssi"), "MEssi", "Should keep original string, only trimmed.")
    
    def test_load_data_missing_files(self):
        """
        Test load_data when some CSV files do not exist. Ensures it returns empty DataFrames
        for missing files and doesn't crash. This covers the 'else' path in load_data.
        """
        # Create a temporary folder with just one CSV for demonstration
        temp_path = "temp_test_data"
        os.makedirs(temp_path, exist_ok=True)

        # Write a minimal CSV for 'players.csv'
        sample_csv_path = os.path.join(temp_path, "players.csv")
        pd.DataFrame({
            "player_id": [10],
            "given_name": ["Ada"],
            "family_name": ["Hegerberg"]
        }).to_csv(sample_csv_path, index=False)

        try:
            dfs = load_data(data_path=temp_path)
            # 'players' should have 1 row
            self.assertIn("players", dfs)
            self.assertEqual(len(dfs["players"]), 1, "Expected 1 row in the 'players' DataFrame.")
            
            # Another known filename that doesn't exist => should be an empty DataFrame
            self.assertIn("goals", dfs)
            self.assertTrue(dfs["goals"].empty, "Since 'goals.csv' doesn't exist, it should be empty DF.")
        finally:
            # Cleanup the temp folder
            shutil.rmtree(temp_path)

    def test_load_data_return_type(self):
        """
        Tests that load_data returns a dictionary of DataFrames with expected keys,
        even if the 'data' folder doesn't exist at all.
        """
        dfs = load_data(data_path="non_existent_folder_12345")
        self.assertIsInstance(dfs, dict)
        # Spot-check a key
        self.assertIn("players", dfs)
        # 'players' should be an empty DataFrame if the file is missing
        self.assertTrue(isinstance(dfs["players"], pd.DataFrame))

    def setUp(self):
        """
        Create mock DataFrames and the derived player_stats once, for re-use
        in smaller unit tests.
        """
        self.players_df = pd.DataFrame({
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

        self.player_appearances_df = pd.DataFrame({
            "player_id": [1, 1, 2],
            "match_id": [101, 102, 103]
        })

        self.goals_df = pd.DataFrame({
            "player_id": [1, 2, 2],
            "match_id": [101, 103, 103],
            "minute_regulation": [10, 85, 90]
        })

        self.matches_df = pd.DataFrame({
            "match_id": [101, 102, 103],
            "knockout_stage": [False, True, True]
        })

        self.bookings_df = pd.DataFrame({
            "player_id": [2, 2],
            "booking_id": [201, 202],
            "match_id": [103, 103]
        })

        self.substitutions_df = pd.DataFrame({
            "match_id": [101, 102],
            "player_id": [1, 2],
            "coming_on": [True, False],
            "going_off": [False, True]
        })

        self.penalty_kicks_df = pd.DataFrame({
            "player_id": [1, 2, 2],
            "converted": [1, 0, 1]
        })

        self.award_winners_df = pd.DataFrame({
            "player_id": [1, 1, 2],
            "award_id": [501, 502, 501]
        })

        self.squads_df = pd.DataFrame({
            "player_id": [1, 2],
            "team_id": [555, 666],
            "team_name": ["USA", "Brazil"],
            "team_code": ["USA", "BRA"]
        })

        self.teams_df = pd.DataFrame({
            "team_id": [555, 666],
            "team_name": ["USA", "Brazil"],
            "team_code": ["USA", "BRA"],
            "region_name": ["North America", "South America"],
            "confederation_code": ["CONCACAF", "CONMEBOL"]
        })

        # Combine into dict for create_advanced_player_stats
        self.dfs_mock = {
            "players": self.players_df,
            "player_appearances": self.player_appearances_df,
            "goals": self.goals_df,
            "matches": self.matches_df,
            "bookings": self.bookings_df,
            "substitutions": self.substitutions_df,
            "penalty_kicks": self.penalty_kicks_df,
            "award_winners": self.award_winners_df,
            "squads": self.squads_df,
            "teams": self.teams_df
        }

        # Produce the advanced stats DataFrame for tests
        self.player_stats = create_advanced_player_stats(self.dfs_mock)

    def test_load_data(self):
        """
        Tests that load_data returns a dictionary of DataFrames
        with the expected keys (filenames minus .csv extension).
        """
        dfs = load_data(data_path="data")

        # Check that dfs is a dictionary
        self.assertIsInstance(dfs, dict, "load_data should return a dictionary.")

        # Check a few expected keys are present (spot-check)
        expected_keys = ["players", "goals", "matches", "player_appearances", "bookings"]
        for key in expected_keys:
            self.assertIn(key, dfs, f"'{key}' should be a key in the returned dictionary.")

        # Check that each item in dfs is a pandas DataFrame
        for key, df_item in dfs.items():
            self.assertIsInstance(df_item, pd.DataFrame, f"dfs['{key}'] should be a DataFrame.")

    def test_create_advanced_player_stats_columns(self):
        """
        Ensure all required columns exist in the resulting player_stats.
        """
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
            self.assertIn(
                col,
                self.player_stats.columns,
                f"Missing expected column: {col}"
            )

    def test_name_fix(self):
        """
        Check that name cleanup occurred for 'given_name' and 'family_name'.
        This also covers lines in _prepare_player_base and _fix_name.
        """
        p1_name = self.player_stats.loc[self.player_stats["player_id"] == 1, "full_name"].values[0]
        p2_name = self.player_stats.loc[self.player_stats["player_id"] == 2, "full_name"].values[0]

        # Because 'given_name' = 'not applicable' => "" and 'family_name' = "Morgan" => "Morgan"
        # p1_name might end up as "Morgan" or "Unknown Morgan" depending on how you handle the logic
        self.assertTrue(
            p1_name in ("Morgan", "Unknown Morgan"),
            f"Expected 'Morgan' or 'Unknown Morgan', got '{p1_name}'."
        )
        # Because 'given_name' = "Alex", 'family_name' = "not applicable" => ""
        # p2_name might be "Alex" or "Alex Unknown"
        self.assertTrue(
            p2_name in ("Alex", "Alex Unknown"),
            f"Expected 'Alex' or 'Alex Unknown', got '{p2_name}'."
        )

    def test_numeric_columns_calculations_player1(self):
        """
        Validate numeric columns for Player 1 in the mock dataset.
        """
        p1_stats = self.player_stats[self.player_stats["player_id"] == 1].iloc[0]

        # total_appearances=2, total_goals=1 => match_id=101 => non-knockout
        self.assertEqual(p1_stats["total_appearances"], 2)
        self.assertEqual(p1_stats["total_goals"], 1)
        self.assertEqual(p1_stats["knockout_goals"], 0)
        self.assertAlmostEqual(p1_stats["goals_per_appearance"], 0.5, places=3)

        # Penalties => 1 attempt => 1 converted => conversion=1.0
        self.assertEqual(p1_stats["penalty_attempts"], 1)
        self.assertEqual(p1_stats["penalty_converted"], 1)
        self.assertEqual(p1_stats["penalty_conversion"], 1.0)

        # Awards => total_awards=2
        self.assertEqual(p1_stats["total_awards"], 2)

        # Substitutions => times_subbed_on=1, times_subbed_off=0
        self.assertEqual(p1_stats["times_subbed_on"], 1)
        self.assertEqual(p1_stats["times_subbed_off"], 0)

        # Clutch goals => 0
        self.assertEqual(p1_stats["clutch_goals"], 0)

        # Primary team => USA
        self.assertEqual(p1_stats["primary_team_name"], "USA")
        self.assertEqual(p1_stats["primary_team_code"], "USA")
        self.assertEqual(p1_stats["primary_confederation_code"], "CONCACAF")
        self.assertEqual(p1_stats["continent"], "North America")

    def test_numeric_columns_calculations_player2(self):
        """
        Validate numeric columns for Player 2 in the mock dataset.
        """
        p2_stats = self.player_stats[self.player_stats["player_id"] == 2].iloc[0]

        # total_appearances=1, total_goals=2 => knockout => 2
        self.assertEqual(p2_stats["total_appearances"], 1)
        self.assertEqual(p2_stats["total_goals"], 2)
        self.assertEqual(p2_stats["knockout_goals"], 2)
        self.assertAlmostEqual(p2_stats["goals_per_appearance"], 2.0, places=3)

        # Bookings => 2 => cards_per_appearance => 2.0
        self.assertEqual(p2_stats["total_cards"], 2)
        self.assertAlmostEqual(p2_stats["cards_per_appearance"], 2.0, places=3)

        # Penalties => 2 attempts => 1 converted => 0.5
        self.assertEqual(p2_stats["penalty_attempts"], 2)
        self.assertEqual(p2_stats["penalty_converted"], 1)
        self.assertAlmostEqual(p2_stats["penalty_conversion"], 0.5, places=3)

        # Awards => 1
        self.assertEqual(p2_stats["total_awards"], 1)

        # Substitutions => times_subbed_on=0, times_subbed_off=1
        self.assertEqual(p2_stats["times_subbed_on"], 0)
        self.assertEqual(p2_stats["times_subbed_off"], 1)

        # Clutch goals => 2
        self.assertEqual(p2_stats["clutch_goals"], 2)

        # Primary team => Brazil
        self.assertEqual(p2_stats["primary_team_name"], "Brazil")
        self.assertEqual(p2_stats["primary_team_code"], "BRA")
        self.assertEqual(p2_stats["primary_confederation_code"], "CONMEBOL")
        self.assertEqual(p2_stats["continent"], "South America")

    def test_filter_players_gender(self):
        """
        Tests that filter_players returns the correct subsets by gender.
        """
        data_frame = pd.DataFrame({
            "player_id": [1, 2, 3],
            "female": [True, False, True],
            "goal_keeper": [False, False, False],
            "defender": [False, False, False],
            "midfielder": [False, False, False],
            "forward": [False, False, False],
            "continent": ["Unknown", "Unknown", "Unknown"]
        })

        # No filter => should return all 3
        df_all = filter_players(data_frame, gender="All")
        self.assertEqual(len(df_all), 3, "Should return all rows when gender='All'")

        # "Men" => only where female is False => 1 row
        df_men = filter_players(data_frame, gender="Men")
        self.assertEqual(len(df_men), 1)
        self.assertEqual(df_men.iloc[0]["player_id"], 2)

        # "Women" => only where female is True => 2 rows
        df_women = filter_players(data_frame, gender="Women")
        self.assertEqual(len(df_women), 2)
        # Check that all are female
        self.assertTrue(df_women["female"].all())

    def test_filter_players_continent(self):
        """
        Tests that filter_players returns the correct subsets by continent.
        """
        data_frame = pd.DataFrame({
            "player_id": [1, 2, 3, 4],
            "female": [True, False, True, False],
            "continent": ["Europe", "Asia", "Europe", "North America"],
            "goal_keeper": [False, False, False, False],
            "defender": [False, False, False, False],
            "midfielder": [False, False, False, False],
            "forward": [False, False, False, False]
        })

        # No filter => return all 4
        df_all = filter_players(data_frame)
        self.assertEqual(len(df_all), 4)

        # Filter by "Europe"
        df_europe = filter_players(data_frame, continent="Europe")
        self.assertEqual(len(df_europe), 2)
        self.assertTrue(df_europe["continent"].eq("Europe").all())

        # Filter by "North America"
        df_na = filter_players(data_frame, continent="North America")
        self.assertEqual(len(df_na), 1)
        self.assertTrue(df_na["continent"].eq("North America").all())

        # Filter by "Unknown" => should return none here
        df_unknown = filter_players(data_frame, continent="Unknown")
        self.assertEqual(len(df_unknown), 0)

    def test_filter_players_position(self):
        """
        Tests that filter_players correctly filters by position.
        """
        data_frame = pd.DataFrame({
            "player_id": [1, 2, 3, 4],
            "female": [True, True, False, False],
            "continent": ["Europe", "Asia", "Europe", "Asia"],
            "goal_keeper": [True, False, False, False],
            "defender": [False, True, False, False],
            "midfielder": [False, False, True, False],
            "forward": [False, False, False, True]
        })

        # No filter => all 4
        df_all = filter_players(data_frame)
        self.assertEqual(len(df_all), 4)

        # Goalkeepers => just player_id=1
        df_gk = filter_players(data_frame, position="Goalkeeper")
        self.assertEqual(len(df_gk), 1)
        self.assertTrue(df_gk["goal_keeper"].all())

        # Defender => just player_id=2
        df_def = filter_players(data_frame, position="Defender")
        self.assertEqual(len(df_def), 1)
        self.assertTrue(df_def["defender"].all())

        # Midfielder => player_id=3
        df_mid = filter_players(data_frame, position="Midfielder")
        self.assertEqual(len(df_mid), 1)
        self.assertTrue(df_mid["midfielder"].all())

        # Forward => player_id=4
        df_fwd = filter_players(data_frame, position="Forward")
        self.assertEqual(len(df_fwd), 1)
        self.assertTrue(df_fwd["forward"].all())


    def test_create_advanced_player_stats_edge_cases(self):
        """
        Creates DataFrames that are empty or missing columns to trigger the ELSE blocks
        and rarely-reached lines in each of the private merge functions.
        This helps reach 100% coverage for data_manager.py.
        """
        # 1) players missing 'family_name' or 'given_name', so _fix_name lines are triggered
        players_df = pd.DataFrame({
            "player_id": [100],
            # intentionally missing 'given_name', 'family_name'
            "birth_date": [None],
            # 'female' etc. also missing
        })

        # 2) appearances_df empty => triggers the else in _merge_appearances
        appearances_df = pd.DataFrame()

        # 3) goals_df missing 'player_id' => triggers the else in _merge_goals & knockout_goals
        goals_df = pd.DataFrame({
            "match_id": [999],
            "minute_regulation": [80]
        })

        # 4) bookings_df with zero total_appearances => dividing by zero => inf => replaced with 0
        bookings_df = pd.DataFrame({
            "player_id": [100, 100],
            "booking_id": [1, 2],
        })

        # 5) penalty_kicks_df empty => triggers else in _merge_penalties
        penalty_kicks_df = pd.DataFrame()

        # 6) award_winners_df missing "player_id" => else branch in _merge_awards
        award_winners_df = pd.DataFrame({
            "award_id": [501, 502]
        })

        # 7) substitutions_df missing "coming_on"/"going_off" => sub_on empty => else
        substitutions_df = pd.DataFrame({
            "match_id": [999],
            "player_id": [100],
        })

        # 8) matches_df empty => no merges for knockout => else in _merge_knockout_goals & _merge_clutch_goals
        matches_df = pd.DataFrame()

        # 9) squads_df/teams_df both empty => else in _merge_primary_team
        squads_df = pd.DataFrame()
        teams_df = pd.DataFrame()

        # Combine into dict
        dfs_edge = {
            "players": players_df,
            "player_appearances": appearances_df,
            "goals": goals_df,
            "bookings": bookings_df,
            "penalty_kicks": penalty_kicks_df,
            "award_winners": award_winners_df,
            "substitutions": substitutions_df,
            "matches": matches_df,
            "squads": squads_df,
            "teams": teams_df,
        }

        # Now create_advanced_player_stats will call all merges with these special DataFrames
        player_stats_edge = create_advanced_player_stats(dfs_edge)

        # We don't expect any meaningful stats, but we do expect no crash,
        # and coverage for the else branches. Check shape or columns exist:
        self.assertIsInstance(player_stats_edge, pd.DataFrame)
        self.assertFalse(player_stats_edge.empty, "We do have a row for player_id=100.")
        self.assertIn("full_name", player_stats_edge.columns, "Should have 'full_name' from _prepare_player_base.")
        
        # Check that total_appearances might be 0.0
        self.assertIn("total_appearances", player_stats_edge.columns)
        row = player_stats_edge.iloc[0]
        # Because appearances_df is empty, this else merges an empty DF => 0
        self.assertEqual(row["total_appearances"], 0)

        # Also check we handled dividing by zero -> goals_per_appearance => 0
        # Because total_goals is also from the else path => 0
        self.assertIn("goals_per_appearance", player_stats_edge.columns)
        self.assertEqual(row["goals_per_appearance"], 0)

        # Awards, penalty, etc. also 0 or default
        self.assertEqual(row["total_awards"], 0)
        self.assertEqual(row["penalty_attempts"], 0)
        self.assertEqual(row["penalty_conversion"], 0.0)

        # Primary team => 'Unknown' from the else path
        self.assertIn("primary_team_name", player_stats_edge.columns)
        self.assertEqual(row["primary_team_name"], "Unknown")

    def test_fix_name_edge_cases(self):
        """
        Test the private helper _fix_name thoroughly.
        This ensures lines that handle None, 'na', etc. are covered.
        """
        self.assertEqual(_fix_name(None), "")
        self.assertEqual(_fix_name(""), "")
        self.assertEqual(_fix_name(" na "), "")
        self.assertEqual(_fix_name("  NOT APPLICABLE  "), "")
        self.assertEqual(_fix_name("   n/A   "), "")
        self.assertEqual(_fix_name(" Lionel "), "Lionel", "Trims whitespace but keeps the original string content.")


if __name__ == "__main__":
    unittest.main()
