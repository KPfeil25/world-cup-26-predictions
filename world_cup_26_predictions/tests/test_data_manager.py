"""
This file contains unit tests for the data_manager.py file.
"""

import os
import unittest
import shutil
import pandas as pd

from player_analytics.data_manager import (
    load_data,
    create_advanced_player_stats,
    filter_players,
    _fix_name
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
        self.assertEqual(
            _fix_name("  Lionel  "),
            "Lionel",
            "Should trim whitespace and preserve case."
        )
        self.assertEqual(
            _fix_name("MEssi"),
            "MEssi",
            "Should keep original string, only trimmed."
        )

    def test_load_data_missing_files(self):
        """
        Test load_data when some CSV files do not exist. Ensures it returns empty DataFrames
        for missing files and doesn't crash. This covers the 'else' path in load_data.
        """
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
            self.assertEqual(len(dfs["players"]), 1, "Expected 1 row in 'players' DataFrame.")
            # Another known filename that doesn't exist => should be an empty DataFrame
            self.assertIn("goals", dfs)
            self.assertTrue(
                dfs["goals"].empty,
                "Since 'goals.csv' doesn't exist, it should be empty DF."
            )
        finally:
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
        self.assertIsInstance(dfs["players"], pd.DataFrame)

    def setUp(self):
        """
        Create mock DataFrames and the derived player_stats once, for re-use
        in smaller unit tests.
        """
        # We will store everything in a single dictionary to avoid too many attributes
        # to avoid pylint complains.
        self.test_data = {}

        self.test_data["players_df"] = pd.DataFrame({
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

        self.test_data["player_appearances_df"] = pd.DataFrame({
            "player_id": [1, 1, 2],
            "match_id": [101, 102, 103]
        })

        self.test_data["goals_df"] = pd.DataFrame({
            "player_id": [1, 2, 2],
            "match_id": [101, 103, 103],
            "minute_regulation": [10, 85, 90]
        })

        self.test_data["matches_df"] = pd.DataFrame({
            "match_id": [101, 102, 103],
            "knockout_stage": [False, True, True]
        })

        self.test_data["bookings_df"] = pd.DataFrame({
            "player_id": [2, 2],
            "booking_id": [201, 202],
            "match_id": [103, 103]
        })

        self.test_data["substitutions_df"] = pd.DataFrame({
            "match_id": [101, 102],
            "player_id": [1, 2],
            "coming_on": [True, False],
            "going_off": [False, True]
        })

        self.test_data["penalty_kicks_df"] = pd.DataFrame({
            "player_id": [1, 2, 2],
            "converted": [1, 0, 1]
        })

        self.test_data["award_winners_df"] = pd.DataFrame({
            "player_id": [1, 1, 2],
            "award_id": [501, 502, 501]
        })

        self.test_data["squads_df"] = pd.DataFrame({
            "player_id": [1, 2],
            "team_id": [555, 666],
            "team_name": ["USA", "Brazil"],
            "team_code": ["USA", "BRA"]
        })

        self.test_data["teams_df"] = pd.DataFrame({
            "team_id": [555, 666],
            "team_name": ["USA", "Brazil"],
            "team_code": ["USA", "BRA"],
            "region_name": ["North America", "South America"],
            "confederation_code": ["CONCACAF", "CONMEBOL"]
        })

        # Combine into a single dict for create_advanced_player_stats.
        self.test_data["dfs_mock"] = {
            "players": self.test_data["players_df"],
            "player_appearances": self.test_data["player_appearances_df"],
            "goals": self.test_data["goals_df"],
            "matches": self.test_data["matches_df"],
            "bookings": self.test_data["bookings_df"],
            "substitutions": self.test_data["substitutions_df"],
            "penalty_kicks": self.test_data["penalty_kicks_df"],
            "award_winners": self.test_data["award_winners_df"],
            "squads": self.test_data["squads_df"],
            "teams": self.test_data["teams_df"]
        }

        # Produce the advanced stats DataFrame for tests
        self.test_data["player_stats"] = create_advanced_player_stats(self.test_data["dfs_mock"])

    def test_load_data(self):
        """
        Tests that load_data returns a dictionary of DataFrames
        with the expected keys (filenames minus .csv extension).
        """
        dfs = load_data(data_path="data")

        self.assertIsInstance(dfs, dict, "load_data should return a dictionary.")

        expected_keys = ["players", "goals", "matches", "player_appearances", "bookings"]
        for key in expected_keys:
            self.assertIn(key, dfs, f"'{key}' should be a key in the returned dictionary.")

        for key, df_item in dfs.items():
            self.assertIsInstance(df_item, pd.DataFrame, f"dfs['{key}'] should be a DataFrame.")

    def test_create_advanced_player_stats_columns(self):
        """
        Ensure all required columns exist in the resulting player_stats.
        """
        player_stats = self.test_data["player_stats"]
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

    def test_name_fix(self):
        """
        Check that name cleanup occurred for 'given_name' and 'family_name'.
        """
        player_stats = self.test_data["player_stats"]

        p1_name = player_stats.loc[player_stats["player_id"] == 1, "full_name"].values[0]
        p2_name = player_stats.loc[player_stats["player_id"] == 2, "full_name"].values[0]

        # Because 'given_name' = 'not applicable' => "" and 'family_name' = "Morgan"
        self.assertTrue(
            p1_name in ("Morgan", "Unknown Morgan"),
            f"Expected 'Morgan' or 'Unknown Morgan', got '{p1_name}'."
        )
        # Because 'given_name' = "Alex", 'family_name' = "not applicable" => ""
        self.assertTrue(
            p2_name in ("Alex", "Alex Unknown"),
            f"Expected 'Alex' or 'Alex Unknown', got '{p2_name}'."
        )

    def test_numeric_columns_calculations_player1(self):
        """
        Validate numeric columns for Player 1 in the mock dataset.
        """
        ps = self.test_data["player_stats"]
        p1_stats = ps[ps["player_id"] == 1].iloc[0]

        self.assertEqual(p1_stats["total_appearances"], 2)
        self.assertEqual(p1_stats["total_goals"], 1)
        self.assertEqual(p1_stats["knockout_goals"], 0)
        self.assertAlmostEqual(p1_stats["goals_per_appearance"], 0.5, places=3)

        self.assertEqual(p1_stats["penalty_attempts"], 1)
        self.assertEqual(p1_stats["penalty_converted"], 1)
        self.assertEqual(p1_stats["penalty_conversion"], 1.0)

        self.assertEqual(p1_stats["total_awards"], 2)
        self.assertEqual(p1_stats["times_subbed_on"], 1)
        self.assertEqual(p1_stats["times_subbed_off"], 0)
        self.assertEqual(p1_stats["clutch_goals"], 0)

        self.assertEqual(p1_stats["primary_team_name"], "USA")
        self.assertEqual(p1_stats["primary_team_code"], "USA")
        self.assertEqual(p1_stats["primary_confederation_code"], "CONCACAF")
        self.assertEqual(p1_stats["continent"], "North America")

    def test_numeric_columns_calculations_player2(self):
        """
        Validate numeric columns for Player 2 in the mock dataset.
        """
        ps = self.test_data["player_stats"]
        p2_stats = ps[ps["player_id"] == 2].iloc[0]

        self.assertEqual(p2_stats["total_appearances"], 1)
        self.assertEqual(p2_stats["total_goals"], 2)
        self.assertEqual(p2_stats["knockout_goals"], 2)
        self.assertAlmostEqual(p2_stats["goals_per_appearance"], 2.0, places=3)

        self.assertEqual(p2_stats["total_cards"], 2)
        self.assertAlmostEqual(p2_stats["cards_per_appearance"], 2.0, places=3)

        self.assertEqual(p2_stats["penalty_attempts"], 2)
        self.assertEqual(p2_stats["penalty_converted"], 1)
        self.assertAlmostEqual(p2_stats["penalty_conversion"], 0.5, places=3)

        self.assertEqual(p2_stats["total_awards"], 1)
        self.assertEqual(p2_stats["times_subbed_on"], 0)
        self.assertEqual(p2_stats["times_subbed_off"], 1)
        self.assertEqual(p2_stats["clutch_goals"], 2)

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

        df_all = filter_players(data_frame, gender="All")
        self.assertEqual(len(df_all), 3, "Should return all rows when gender='All'")

        df_men = filter_players(data_frame, gender="Men")
        self.assertEqual(len(df_men), 1)
        self.assertEqual(df_men.iloc[0]["player_id"], 2)

        df_women = filter_players(data_frame, gender="Women")
        self.assertEqual(len(df_women), 2)
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

        df_all = filter_players(data_frame)
        self.assertEqual(len(df_all), 4)

        df_europe = filter_players(data_frame, continent="Europe")
        self.assertEqual(len(df_europe), 2)
        self.assertTrue(df_europe["continent"].eq("Europe").all())

        df_na = filter_players(data_frame, continent="North America")
        self.assertEqual(len(df_na), 1)
        self.assertTrue(df_na["continent"].eq("North America").all())

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

        df_all = filter_players(data_frame)
        self.assertEqual(len(df_all), 4)

        df_gk = filter_players(data_frame, position="Goalkeeper")
        self.assertEqual(len(df_gk), 1)
        self.assertTrue(df_gk["goal_keeper"].all())

        df_def = filter_players(data_frame, position="Defender")
        self.assertEqual(len(df_def), 1)
        self.assertTrue(df_def["defender"].all())

        df_mid = filter_players(data_frame, position="Midfielder")
        self.assertEqual(len(df_mid), 1)
        self.assertTrue(df_mid["midfielder"].all())

        df_fwd = filter_players(data_frame, position="Forward")
        self.assertEqual(len(df_fwd), 1)
        self.assertTrue(df_fwd["forward"].all())

    def test_create_advanced_player_stats_edge_cases(self):
        """
        Creates DataFrames that are empty or missing columns to trigger the ELSE blocks
        and rarely-reached lines in each of the private merge functions.
        """
        players_df = pd.DataFrame({
            "player_id": [100],
            # intentionally missing 'given_name', 'family_name'
            "birth_date": [None]
        })

        appearances_df = pd.DataFrame()  # triggers else in _merge_appearances
        goals_df = pd.DataFrame({"match_id": [999], "minute_regulation": [80]})
        bookings_df = pd.DataFrame({"player_id": [100, 100], "booking_id": [1, 2]})
        penalty_kicks_df = pd.DataFrame()
        award_winners_df = pd.DataFrame({"award_id": [501, 502]})
        substitutions_df = pd.DataFrame({"match_id": [999], "player_id": [100]})
        matches_df = pd.DataFrame()
        squads_df = pd.DataFrame()
        teams_df = pd.DataFrame()

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

        player_stats_edge = create_advanced_player_stats(dfs_edge)

        self.assertIsInstance(player_stats_edge, pd.DataFrame)
        self.assertFalse(player_stats_edge.empty, "We do have a row for player_id=100.")
        self.assertIn("full_name", player_stats_edge.columns)
        row = player_stats_edge.iloc[0]
        self.assertEqual(row["total_appearances"], 0)
        self.assertEqual(row["total_goals"], 0)
        self.assertEqual(row["goals_per_appearance"], 0)
        self.assertEqual(row["total_awards"], 0)
        self.assertEqual(row["penalty_attempts"], 0)
        self.assertEqual(row["penalty_conversion"], 0.0)
        self.assertEqual(row["primary_team_name"], "Unknown")

    def test_fix_name_edge_cases(self):
        """
        Test the private helper _fix_name thoroughly.
        """
        self.assertEqual(_fix_name(None), "")
        self.assertEqual(_fix_name(""), "")
        self.assertEqual(_fix_name(" na "), "")
        self.assertEqual(_fix_name("  NOT APPLICABLE  "), "")
        self.assertEqual(_fix_name("   n/A   "), "")
        self.assertEqual(_fix_name(" Lionel "), "Lionel")


if __name__ == "__main__":
    unittest.main()
