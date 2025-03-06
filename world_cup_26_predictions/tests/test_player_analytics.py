# pylint: disable=too-many-public-methods
"""
This is a test file with many public methods to cover
a wide range of test cases, so enforcing a strict limit isn’t necessary here.
Disabling this check helps keep the focus on thorough testing rather than
adhering to a strict code style guideline.

This file tests the player_analytics.py module, which contains functions for
analyzing and visualizing player statistics.
"""

import unittest
import pandas as pd
from plotly.graph_objects import Figure

# Adjust the import path as needed if your structure differs
from player_analytics.player_analytics import (
    plot_top_scorers,
    plot_top_knockout_scorers,
    plot_goals_per_appearance,
    plot_most_awarded_players,
    plot_best_penalty_conversion,
    plot_highest_card_rate,
    plot_substitution_patterns,
    plot_position_appearances,
    compare_players,
    plot_compare_players_side_by_side,
    plot_comparison_radar,
    plot_top_clutch_scorers,
    plot_top_impact_players,
)

class TestPlayerAnalytics(unittest.TestCase):
    """
    TestCase for verifying functionality of the player_analytics.py module.
    """

    def setUp(self):
        """
        Creates a small sample DataFrame for testing the analytics functions.
        """
        data = {
            "full_name": ["Player A", "Player B", "Player C", "Player D", "Player E"],
            "total_goals": [10, 20, 15, 5, 0],
            "knockout_goals": [2, 5, 3, 1, 0],
            "goals_per_appearance": [0.5, 0.3, 0.75, 0.1, 0],
            "total_appearances": [20, 66, 20, 50, 10],
            "cards_per_appearance": [0.1, 0.05, 0.2, 0, 0.1],
            "penalty_attempts": [2, 0, 5, 1, 3],
            "penalty_conversion": [0.5, 0, 0.8, 1, 0.67],
            "penalty_converted": [1, 0, 4, 1, 2],
            "total_awards": [3, 2, 4, 1, 0],
            "times_subbed_on": [5, 2, 1, 7, 0],
            "times_subbed_off": [2, 3, 0, 1, 5],
            "subbed_on_goals": [1, 0, 0, 2, 0],
            "clutch_goals": [2, 1, 3, 0, 0],
            "player_id": [1001, 1002, 1003, 1004, 1005],
            "continent": ["Europe", "South America", "Europe", "Africa", "Asia"],
            "total_cards": [2, 3, 4, 0, 1],
            "goal_keeper": [False, False, False, True, False],
            "defender": [False, False, True, False, False],
            "midfielder": [False, True, False, False, False],
            "forward": [True, False, False, False, True],
        }
        self.sample_data = pd.DataFrame(data)

    def test_plot_top_scorers_empty(self):
        """
        plot_top_scorers should return None if the DataFrame is empty.
        """
        df_empty = pd.DataFrame()
        fig = plot_top_scorers(df_empty)
        self.assertIsNone(fig)

    def test_plot_top_scorers_valid(self):
        """
        plot_top_scorers should return a Figure when valid data is provided.
        """
        fig = plot_top_scorers(self.sample_data, top_n=3, color_by="continent")
        self.assertIsInstance(fig, Figure)

    def test_plot_top_knockout_scorers_empty(self):
        """
        plot_top_knockout_scorers should return None if the DataFrame is empty.
        """
        df_empty = pd.DataFrame()
        fig = plot_top_knockout_scorers(df_empty)
        self.assertIsNone(fig)

    def test_plot_top_knockout_scorers_valid(self):
        """
        plot_top_knockout_scorers should return a Figure with valid data.
        """
        fig = plot_top_knockout_scorers(self.sample_data, top_n=2)
        self.assertIsInstance(fig, Figure)

    def test_plot_goals_per_appearance_empty(self):
        """
        plot_goals_per_appearance should return None if eligible subset is empty.
        """
        df_empty = pd.DataFrame(columns=["total_appearances"])
        fig = plot_goals_per_appearance(df_empty)
        self.assertIsNone(fig)

    def test_plot_goals_per_appearance_valid(self):
        """
        plot_goals_per_appearance should return a Figure when there's enough data.
        """
        fig = plot_goals_per_appearance(self.sample_data, min_appearances=10, top_n=2)
        self.assertIsInstance(fig, Figure)

    def test_plot_most_awarded_players_empty(self):
        """
        plot_most_awarded_players should return None if subset is empty.
        """
        df_empty = pd.DataFrame(columns=["total_awards"])
        fig = plot_most_awarded_players(df_empty)
        self.assertIsNone(fig)

    def test_plot_most_awarded_players_valid(self):
        """
        plot_most_awarded_players should return a Figure if data is present.
        """
        fig = plot_most_awarded_players(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_best_penalty_conversion_empty(self):
        """
        plot_best_penalty_conversion should return None if no data or no eligible player.
        """
        df_empty = pd.DataFrame(columns=["penalty_attempts"])
        fig_empty = plot_best_penalty_conversion(df_empty)
        self.assertIsNone(fig_empty)

        df_no_eligible = pd.DataFrame({
            "full_name": ["X"],
            "penalty_attempts": [0],
            "penalty_conversion": [0]
        })
        fig_ineligible = plot_best_penalty_conversion(df_no_eligible, min_attempts=1)
        self.assertIsNone(fig_ineligible)

    def test_plot_best_penalty_conversion_valid(self):
        """
        plot_best_penalty_conversion should return a Figure with valid data.
        """
        fig = plot_best_penalty_conversion(self.sample_data, min_attempts=1, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_highest_card_rate_empty(self):
        """
        plot_highest_card_rate returns None if no players meet min_appearances.
        """
        df_empty = pd.DataFrame(columns=["total_appearances"])
        fig_empty = plot_highest_card_rate(df_empty)
        self.assertIsNone(fig_empty)

        df_ineligible = pd.DataFrame({
            "full_name": ["X"],
            "total_appearances": [5],
            "cards_per_appearance": [0.1]
        })
        fig_ineligible = plot_highest_card_rate(df_ineligible, min_appearances=10)
        self.assertIsNone(fig_ineligible)

    def test_plot_highest_card_rate_valid(self):
        """
        plot_highest_card_rate should return a Figure when data is valid.
        """
        fig = plot_highest_card_rate(self.sample_data, min_appearances=10, top_n=2)
        self.assertIsInstance(fig, Figure)

    def test_plot_substitution_patterns_empty(self):
        """
        plot_substitution_patterns should return (None, None) if empty.
        """
        df_empty = pd.DataFrame()
        fig_on, fig_off = plot_substitution_patterns(df_empty)
        self.assertIsNone(fig_on)
        self.assertIsNone(fig_off)

    def test_plot_substitution_patterns_valid(self):
        """
        plot_substitution_patterns should return two Figures with valid data.
        """
        fig_on, fig_off = plot_substitution_patterns(self.sample_data, top_n=2)
        self.assertIsInstance(fig_on, Figure)
        self.assertIsInstance(fig_off, Figure)

    def test_plot_position_appearances_empty(self):
        """
        plot_position_appearances should return None if no players in position.
        """
        df_empty = pd.DataFrame()
        fig = plot_position_appearances(df_empty, "goal_keeper")
        self.assertIsNone(fig)

        df_no_gk = pd.DataFrame({
            "full_name": ["X"],
            "goal_keeper": [False],
            "total_appearances": [10]
        })
        fig_no_gk = plot_position_appearances(df_no_gk, "goal_keeper")
        self.assertIsNone(fig_no_gk)

    def test_plot_position_appearances_valid(self):
        """
        plot_position_appearances should return a Figure if position is present.
        """
        fig = plot_position_appearances(self.sample_data, "goal_keeper")
        self.assertIsInstance(fig, Figure)

    def test_compare_players_empty(self):
        """
        compare_players should return empty DataFrame if stats or selected players are invalid.
        """
        df_empty = pd.DataFrame()
        result_empty = compare_players(df_empty, ["Player A"])
        self.assertTrue(result_empty.empty)

        # No matching names
        df_nomatch = pd.DataFrame({"full_name": ["Z"], "total_goals": [1]})
        result_nomatch = compare_players(df_nomatch, ["Player A"])
        self.assertTrue(result_nomatch.empty)

    def test_compare_players_valid(self):
        """
        compare_players should return the requested players sorted by total_goals desc.
        """
        selected = ["Player A", "Player C"]
        df_comp = compare_players(self.sample_data, selected)
        # Just ensure it's not empty if there's a match
        self.assertFalse(df_comp.empty)

        expected_cols = [
            "player_id", "full_name", "continent",
            "total_appearances", "total_goals", "knockout_goals",
            "goals_per_appearance", "total_cards", "cards_per_appearance",
            "penalty_attempts", "penalty_converted", "penalty_conversion",
            "total_awards", "times_subbed_on", "times_subbed_off",
            "subbed_on_goals", "clutch_goals"
        ]
        for col in expected_cols:
            self.assertIn(col, df_comp.columns)

    def test_plot_compare_players_side_by_side_empty(self):
        """
        plot_compare_players_side_by_side returns None if no matching players.
        """
        df_empty = pd.DataFrame()
        fig_empty = plot_compare_players_side_by_side(df_empty, ["Player A"])
        self.assertIsNone(fig_empty)

        df_nomatch = pd.DataFrame({"full_name": ["Z"], "total_goals": [5]})
        fig_nomatch = plot_compare_players_side_by_side(df_nomatch, ["Player A"])
        self.assertIsNone(fig_nomatch)

    def test_plot_compare_players_side_by_side_valid(self):
        """
        plot_compare_players_side_by_side returns a Figure if players exist.
        """
        fig = plot_compare_players_side_by_side(self.sample_data, ["Player A", "Player B"])
        self.assertIsInstance(fig, Figure)

    def test_plot_comparison_radar_empty(self):
        """
        plot_comparison_radar returns None if no matching players or empty DataFrame.
        """
        df_empty = pd.DataFrame()
        fig_empty = plot_comparison_radar(df_empty, ["Player A"])
        self.assertIsNone(fig_empty)

    def test_plot_comparison_radar_valid(self):
        """
        plot_comparison_radar returns a Figure for up to 5 players.
        """
        fig = plot_comparison_radar(self.sample_data, ["Player A", "Player B", "Player C"])
        self.assertIsInstance(fig, Figure)
        # We expect up to 3 traces
        self.assertEqual(len(fig.data), 3)

    def test_plot_top_clutch_scorers_empty(self):
        """
        plot_top_clutch_scorers returns None if data is empty or missing 'clutch_goals'.
        """
        df_empty = pd.DataFrame()
        fig_empty = plot_top_clutch_scorers(df_empty)
        self.assertIsNone(fig_empty)

        df_no_clutch = pd.DataFrame({"full_name": ["X"], "total_goals": [5]})
        fig_no_clutch = plot_top_clutch_scorers(df_no_clutch)
        self.assertIsNone(fig_no_clutch)

    def test_plot_top_clutch_scorers_valid(self):
        """
        plot_top_clutch_scorers returns a Figure for the given top_n.
        """
        fig = plot_top_clutch_scorers(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_top_impact_players_empty(self):
        """
        plot_top_impact_players returns None if data is empty or missing 'subbed_on_goals'.
        """
        df_empty = pd.DataFrame()
        fig_empty = plot_top_impact_players(df_empty)
        self.assertIsNone(fig_empty)

        df_no_subbed = pd.DataFrame({"full_name": ["X"], "total_goals": [2]})
        fig_no_subbed = plot_top_impact_players(df_no_subbed)
        self.assertIsNone(fig_no_subbed)

    def test_plot_top_impact_players_valid(self):
        """
        plot_top_impact_players returns a Figure for the given top_n.
        """
        fig = plot_top_impact_players(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_top_scorers_missing_columns(self):
        """
        Forces plot_top_scorers to return None because 'total_goals' is missing.
        """
        df_missing_goals = pd.DataFrame({"full_name": ["Player 1"]})
        self.assertIsNone(plot_top_scorers(df_missing_goals))

    def test_plot_top_scorers_nan_column(self):
        """
        Forces plot_top_scorers to coerce total_goals to numeric, but all NaN => return None.
        """
        df_all_nan = pd.DataFrame({
            "full_name": ["A", "B"],
            "total_goals": [float('nan'), float('nan')]
        })
        self.assertIsNone(plot_top_scorers(df_all_nan))

    def test_plot_top_knockout_scorers_missing_column(self):
        """
        'knockout_goals' missing => should return None.
        """
        df_missing = pd.DataFrame({"full_name": ["Player X"]})
        self.assertIsNone(plot_top_knockout_scorers(df_missing))

    def test_plot_goals_per_appearance_no_eligible_players(self):
        """
        Even if columns exist, if no players meet min_appearances => early return None.
        """
        df_mock = pd.DataFrame({
            "full_name": ["X", "Y"],
            "goals_per_appearance": [0.5, 0.7],
            "total_appearances": [5, 8],  # All < min_appearances=10
        })
        self.assertIsNone(plot_goals_per_appearance(df_mock, min_appearances=10))

    def test_plot_most_awarded_players_missing_full_name(self):
        """
        'full_name' missing => immediate return None.
        """
        df_missing = pd.DataFrame({"total_awards": [5, 6, 7]})
        self.assertIsNone(plot_most_awarded_players(df_missing))

    def test_plot_most_awarded_players_all_nan_awards(self):
        """
        total_awards is present but entirely NaN => returns None after coercion.
        """
        df_nan_awards = pd.DataFrame({
            "full_name": ["A", "B"],
            "total_awards": [float('nan'), float('nan')]
        })
        self.assertIsNone(plot_most_awarded_players(df_nan_awards))

    def test_plot_best_penalty_conversion_missing_columns(self):
        """
        Missing 'penalty_conversion' or 'penalty_attempts' => None.
        """
        df_missing = pd.DataFrame({"full_name": ["X"], "penalty_attempts": [1]})
        self.assertIsNone(plot_best_penalty_conversion(df_missing))
        df_missing2 = pd.DataFrame({"full_name": ["X"], "penalty_conversion": [0.5]})
        self.assertIsNone(plot_best_penalty_conversion(df_missing2))

    def test_plot_highest_card_rate_ineligible_data(self):
        """
        Everyone below min_appearances => returns None.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "cards_per_appearance": [0.1, 0.2],
            "total_appearances": [1, 9]
        })
        self.assertIsNone(plot_highest_card_rate(df_mock, min_appearances=10))

    def test_plot_substitution_patterns_missing_columns(self):
        """
        If 'full_name' or 'times_subbed_on' etc. not present => returns (None, None).
        """
        df_missing = pd.DataFrame({"times_subbed_on": [1], "times_subbed_off": [1]})
        # missing 'full_name'
        fig_on, fig_off = plot_substitution_patterns(df_missing)
        self.assertIsNone(fig_on)
        self.assertIsNone(fig_off)

    def test_plot_substitution_patterns_numeric_empty_after_coercion(self):
        """
        times_subbed_on is all NaN => empty after dropna => returns (None, None).
        """
        df_all_nan = pd.DataFrame({
            "full_name": ["A", "B"],
            "times_subbed_on": [float('nan'), float('nan')],
            "times_subbed_off": [0, 1]
        })
        fig_on, fig_off = plot_substitution_patterns(df_all_nan)
        # We expect both to be None if 'times_subbed_on' is all NaN
        self.assertIsNone(fig_on)
        self.assertIsNone(fig_off)

    def test_plot_position_appearances_missing_position_col(self):
        """
        Missing 'goal_keeper' => None.
        """
        df_missing = pd.DataFrame({
            "full_name": ["X"],
            "total_appearances": [10]
        })
        self.assertIsNone(plot_position_appearances(df_missing, "goal_keeper"))

    def test_compare_players_missing_total_goals(self):
        """
        If 'total_goals' is missing, returns empty DataFrame immediately.
        """
        df_missing = pd.DataFrame({
            "full_name": ["A", "B"]
        })
        result = compare_players(df_missing, ["A"])
        self.assertTrue(result.empty)

    def test_plot_compare_players_side_by_side_missing_required_stat(self):
        """
        'knockout_goals' or any stats_of_interest missing => return None.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "total_goals": [10, 20],
            # missing 'knockout_goals'
        })
        fig = plot_compare_players_side_by_side(df_mock, ["P1", "P2"])
        self.assertIsNone(fig)

    def test_plot_compare_players_side_by_side_empty_after_isin(self):
        """
        If no matches in selected_players => returns None.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "total_goals": [5, 5]
        })
        fig = plot_compare_players_side_by_side(df_mock, ["P3", "P4"])
        self.assertIsNone(fig)

    def test_plot_comparison_radar_missing_one_col(self):
        """
        If any of needed_cols is missing => return None.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "goals_per_appearance": [0.5, 0.7],
            "knockout_goals": [1, 2],
            # missing "cards_per_appearance"
        })
        fig = plot_comparison_radar(df_mock, ["P1"])
        self.assertIsNone(fig)

    def test_plot_comparison_radar_more_than_five_players(self):
        """
        Ensures df_radar.head(5) is tested. We pass 6 players and only
        the first 5 get plotted.
        """
        df_6 = pd.DataFrame({
            "full_name": [f"P{i}" for i in range(6)],
            "goals_per_appearance": [0.5, 0.6, 0.7, 0.8, 0.3, 0.4],
            "knockout_goals": [1, 2, 3, 4, 1, 1],
            "cards_per_appearance": [0.1, 0, 0.2, 0.1, 0.05, 0],
            "penalty_conversion": [0.5, 0.8, 1, 0.2, 0.9, 0.3],
            "total_awards": [2, 3, 4, 1, 5, 2],
            "subbed_on_goals": [1, 0, 2, 3, 0, 0],
        })
        fig = plot_comparison_radar(df_6, ["P0", "P1", "P2", "P3", "P4", "P5"])
        self.assertIsInstance(fig, Figure)
        # Should only contain 5 traces
        self.assertEqual(len(fig.data), 5)

    def test_plot_top_clutch_scorers_all_nan(self):
        """
        If 'clutch_goals' is all NaN => return None.
        """
        df_nan = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "clutch_goals": [float('nan'), float('nan')]
        })
        self.assertIsNone(plot_top_clutch_scorers(df_nan))

    def test_plot_top_impact_players_missing_subbed_on_goals(self):
        """
        If 'subbed_on_goals' missing => returns None.
        """
        df_missing = pd.DataFrame({"full_name": ["X"], "total_goals": [2]})
        fig = plot_top_impact_players(df_missing)
        self.assertIsNone(fig)


if __name__ == "__main__":
    unittest.main()
