"""
Unit tests for the updated player_analytics.py module,
which contains functions for analyzing and visualizing player statistics.
"""

import unittest
import pandas as pd
from plotly.graph_objects import Figure

from world_cup_26_predictions.player_analytics.player_analytics import (
    STATS_OF_INTEREST,
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


class BaseTestAnalytics(unittest.TestCase):
    """
    Base class that sets up a sample DataFrame for use by all test classes.
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


class TestTopScorers(BaseTestAnalytics):
    """
    Tests related to plot_top_scorers and plot_top_knockout_scorers.
    """

    def test_plot_top_scorers_empty(self):
        """
        Tests that plot_top_scorers returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        fig = plot_top_scorers(df_empty)
        self.assertIsNone(fig)

    def test_plot_top_scorers_valid(self):
        """
        Tests that plot_top_scorers returns a Figure when given a valid DataFrame.
        """
        fig = plot_top_scorers(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_top_scorers_missing_columns(self):
        """
        Tests that plot_top_scorers returns None when a required column is missing.
        """
        df_missing_goals = pd.DataFrame({"full_name": ["Player 1"]})
        self.assertIsNone(plot_top_scorers(df_missing_goals))

    def test_plot_top_scorers_nan_column(self):
        """
        Tests that plot_top_scorers returns None when a column contains NaN values.
        """
        df_all_nan = pd.DataFrame({
            "full_name": ["A", "B"],
            "total_goals": [float('nan'), float('nan')]
        })
        self.assertIsNone(plot_top_scorers(df_all_nan))

    def test_plot_top_knockout_scorers_empty(self):
        """
        Tests that plot_top_knockout_scorers returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        fig = plot_top_knockout_scorers(df_empty)
        self.assertIsNone(fig)

    def test_plot_top_knockout_scorers_valid(self):
        """
        Tests that plot_top_knockout_scorers returns a Figure when given a valid DataFrame.
        """
        fig = plot_top_knockout_scorers(self.sample_data, top_n=2)
        self.assertIsInstance(fig, Figure)

    def test_plot_top_knockout_scorers_missing_column(self):
        """
        Tests that plot_top_knockout_scorers returns None when a required column is missing.
        """
        df_missing = pd.DataFrame({"full_name": ["Player X"]})
        self.assertIsNone(plot_top_knockout_scorers(df_missing))


class TestGoalsPerAppearance(BaseTestAnalytics):
    """
    Tests related to plot_goals_per_appearance.
    """

    def test_plot_goals_per_appearance_empty(self):
        """
        Tests that plot_goals_per_appearance returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame(columns=["total_appearances"])
        fig = plot_goals_per_appearance(df_empty)
        self.assertIsNone(fig)

    def test_plot_goals_per_appearance_valid(self):
        """
        Tests that plot_goals_per_appearance returns a Figure when given a valid DataFrame.
        """
        fig = plot_goals_per_appearance(self.sample_data, min_appearances=10, top_n=2)
        self.assertIsInstance(fig, Figure)

    def test_plot_goals_per_appearance_no_eligible_players(self):
        """
        Tests that plot_goals_per_appearance returns None when there are no eligible players.
        """
        df_mock = pd.DataFrame({
            "full_name": ["X", "Y"],
            "goals_per_appearance": [0.5, 0.7],
            "total_appearances": [5, 8]
        })
        self.assertIsNone(plot_goals_per_appearance(df_mock, min_appearances=10))


class TestMostAwardedPlayers(BaseTestAnalytics):
    """
    Tests related to plot_most_awarded_players.
    """

    def test_plot_most_awarded_players_empty(self):
        """
        Tests that plot_most_awarded_players returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame(columns=["total_awards"])
        fig = plot_most_awarded_players(df_empty)
        self.assertIsNone(fig)

    def test_plot_most_awarded_players_valid(self):
        """
        Tests that plot_most_awarded_players returns a Figure when given a valid DataFrame.
        """
        fig = plot_most_awarded_players(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_most_awarded_players_missing_full_name(self):
        """
        Tests that plot_most_awarded_players returns None when a required column is missing.
        """
        df_missing = pd.DataFrame({"total_awards": [5, 6, 7]})
        self.assertIsNone(plot_most_awarded_players(df_missing))

    def test_plot_most_awarded_players_all_nan_awards(self):
        """
        Tests that plot_most_awarded_players returns None when all awards are NaN.
        """
        df_nan_awards = pd.DataFrame({
            "full_name": ["A", "B"],
            "total_awards": [float('nan'), float('nan')]
        })
        self.assertIsNone(plot_most_awarded_players(df_nan_awards))


class TestBestPenaltyConversion(BaseTestAnalytics):
    """
    Tests related to plot_best_penalty_conversion.
    """

    def test_plot_best_penalty_conversion_empty(self):
        """
        Tests that plot_best_penalty_conversion returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame(columns=["penalty_attempts"])
        self.assertIsNone(plot_best_penalty_conversion(df_empty))

        df_no_eligible = pd.DataFrame({
            "full_name": ["X"],
            "penalty_attempts": [0],
            "penalty_conversion": [0]
        })
        self.assertIsNone(plot_best_penalty_conversion(df_no_eligible, min_attempts=1))

    def test_plot_best_penalty_conversion_valid(self):
        """
        Tests that plot_best_penalty_conversion returns a Figure when given a valid DataFrame.
        """
        fig = plot_best_penalty_conversion(self.sample_data, min_attempts=1, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_best_penalty_conversion_missing_columns(self):
        """
        Tests that plot_best_penalty_conversion returns None when a required column is missing.
        """
        df_missing = pd.DataFrame({"full_name": ["X"], "penalty_attempts": [1]})
        self.assertIsNone(plot_best_penalty_conversion(df_missing))

        df_missing2 = pd.DataFrame({"full_name": ["X"], "penalty_conversion": [0.5]})
        self.assertIsNone(plot_best_penalty_conversion(df_missing2))


class TestHighestCardRate(BaseTestAnalytics):
    """
    Tests related to plot_highest_card_rate.
    """

    def test_plot_highest_card_rate_empty(self):
        """
        Tests that plot_highest_card_rate returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame(columns=["total_appearances"])
        self.assertIsNone(plot_highest_card_rate(df_empty))

        df_ineligible = pd.DataFrame({
            "full_name": ["X"],
            "total_appearances": [5],
            "cards_per_appearance": [0.1]
        })
        self.assertIsNone(plot_highest_card_rate(df_ineligible, min_appearances=10))

    def test_plot_highest_card_rate_valid(self):
        """
        Tests that plot_highest_card_rate returns a Figure when given a valid DataFrame.
        """
        fig = plot_highest_card_rate(self.sample_data, min_appearances=10, top_n=2)
        self.assertIsInstance(fig, Figure)

    def test_plot_highest_card_rate_ineligible_data(self):
        """
        Tests that plot_highest_card_rate returns None when there are no eligible players.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "cards_per_appearance": [0.1, 0.2],
            "total_appearances": [1, 9]
        })
        self.assertIsNone(plot_highest_card_rate(df_mock, min_appearances=10))


class TestSubstitutionPatterns(BaseTestAnalytics):
    """
    Tests related to plot_substitution_patterns.
    """

    def test_plot_substitution_patterns_empty(self):
        """
        Tests that plot_substitution_patterns returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        fig_on, fig_off = plot_substitution_patterns(df_empty)
        self.assertIsNone(fig_on)
        self.assertIsNone(fig_off)

    def test_plot_substitution_patterns_valid(self):
        """
        Tests that plot_substitution_patterns returns two Figures when given a valid DataFrame.
        """
        fig_on, fig_off = plot_substitution_patterns(self.sample_data, top_n=2)
        self.assertIsInstance(fig_on, Figure)
        self.assertIsInstance(fig_off, Figure)

    def test_plot_substitution_patterns_missing_columns(self):
        """
        Tests that plot_substitution_patterns returns None when a required column is missing.
        """
        df_missing = pd.DataFrame({"times_subbed_on": [1], "times_subbed_off": [1]})
        fig_on, fig_off = plot_substitution_patterns(df_missing)
        self.assertIsNone(fig_on)
        self.assertIsNone(fig_off)

    def test_plot_substitution_patterns_numeric_empty_after_coercion(self):
        """
        Tests that plot_substitution_patterns returns None when a required column
        is missing.
        """
        df_all_nan = pd.DataFrame({
            "full_name": ["A", "B"],
            "times_subbed_on": [float('nan'), float('nan')],
            "times_subbed_off": [0, 1]
        })
        fig_on, fig_off = plot_substitution_patterns(df_all_nan)
        self.assertIsNone(fig_on)
        self.assertIsNone(fig_off)


class TestPositionAppearances(BaseTestAnalytics):
    """
    Tests related to plot_position_appearances.
    """

    def test_plot_position_appearances_empty(self):
        """
        Tests that plot_position_appearances returns None when given an empty DataFrame.
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
        Tests that plot_position_appearances returns a Figure when given a valid DataFrame.
        """
        fig = plot_position_appearances(self.sample_data, "goal_keeper")
        self.assertIsInstance(fig, Figure)

    def test_plot_position_appearances_missing_position_col(self):
        """
        Tests that plot_position_appearances returns None when a required column is missing.
        """
        df_missing = pd.DataFrame({
            "full_name": ["X"],
            "total_appearances": [10]
        })
        self.assertIsNone(plot_position_appearances(df_missing, "goal_keeper"))


class TestComparePlayers(BaseTestAnalytics):
    """
    Tests related to compare_players().
    """

    def test_compare_players_empty(self):
        """
        Tests that compare_players returns an empty DataFrame when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        result_empty = compare_players(df_empty, ["Player A"])
        self.assertTrue(result_empty.empty)

        df_nomatch = pd.DataFrame({"full_name": ["Z"], "total_goals": [1]})
        result_nomatch = compare_players(df_nomatch, ["Player A"])
        self.assertTrue(result_nomatch.empty)

    def test_compare_players_valid(self):
        """
        Tests that compare_players returns a DataFrame when given a valid DataFrame.
        """
        selected = ["Player A", "Player C"]
        df_comp = compare_players(self.sample_data, selected)
        self.assertFalse(df_comp.empty)

        for col in STATS_OF_INTEREST:
            if col in df_comp.columns:
                self.assertIn(col, df_comp.columns)

    def test_compare_players_missing_total_goals(self):
        """
        Tests that compare_players returns an empty DataFrame when total_goals is missing.
        """
        df_missing = pd.DataFrame({"full_name": ["A", "B"]})
        result = compare_players(df_missing, ["A"])
        self.assertTrue(result.empty)


class TestPlotComparePlayersSideBySide(BaseTestAnalytics):
    """
    Tests related to plot_compare_players_side_by_side().
    """

    def test_plot_compare_players_side_by_side_empty(self):
        """
        Tests that plot_compare_players_side_by_side returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        fig_empty = plot_compare_players_side_by_side(df_empty, ["Player A"])
        self.assertIsNone(fig_empty)

        df_nomatch = pd.DataFrame({"full_name": ["Z"], "total_goals": [5]})
        fig_nomatch = plot_compare_players_side_by_side(df_nomatch, ["Player A"])
        self.assertIsNone(fig_nomatch)

    def test_plot_compare_players_side_by_side_valid(self):
        """
        Tests that plot_compare_players_side_by_side returns a Figure when given a valid DataFrame.
        """
        fig = plot_compare_players_side_by_side(
            self.sample_data, ["Player A", "Player B"]
        )
        self.assertIsInstance(fig, Figure)

    def test_plot_compare_players_side_by_side_missing_required_stat(self):
        """
        Tests that plot_compare_players_side_by_side returns None when a required column is missing.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "total_goals": [10, 20],
            # 'knockout_goals' is missing
        })
        fig = plot_compare_players_side_by_side(df_mock, ["P1", "P2"])
        self.assertIsNone(fig)

    def test_plot_compare_players_side_by_side_empty_after_isin(self):
        """
        Tests that plot_compare_players_side_by_side returns None when there are no
        eligible players.
        """
        df_mock = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "total_goals": [5, 5]
        })
        fig = plot_compare_players_side_by_side(df_mock, ["P3", "P4"])
        self.assertIsNone(fig)


class TestPlotComparisonRadar(BaseTestAnalytics):
    """
    Tests related to plot_comparison_radar().
    """

    def test_plot_comparison_radar_empty(self):
        """
        Tests that plot_comparison_radar returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        fig_empty = plot_comparison_radar(df_empty, ["Player A"])
        self.assertIsNone(fig_empty)

    def test_plot_comparison_radar_valid(self):
        """
        Tests that plot_comparison_radar returns a Figure when given a valid DataFrame.
        """
        fig = plot_comparison_radar(self.sample_data, ["Player A", "Player B", "Player C"])
        self.assertIsInstance(fig, Figure)
        self.assertEqual(len(fig.data), 3)

    def test_plot_comparison_radar_missing_one_col(self):
        """
        Tests that plot_comparison_radar returns None when a required column is missing.
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
        Tests that plot_comparison_radar returns a Figure when given a DataFrame
        with more than 5 players.
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
        fig = plot_comparison_radar(
            df_6, ["P0", "P1", "P2", "P3", "P4", "P5"]
        )
        self.assertIsInstance(fig, Figure)
        self.assertEqual(len(fig.data), 5)


class TestTopClutchScorers(BaseTestAnalytics):
    """
    Tests related to plot_top_clutch_scorers().
    """

    def test_plot_top_clutch_scorers_empty(self):
        """
        Tests that plot_top_clutch_scorers returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        self.assertIsNone(plot_top_clutch_scorers(df_empty))

        df_no_clutch = pd.DataFrame({"full_name": ["X"], "total_goals": [5]})
        self.assertIsNone(plot_top_clutch_scorers(df_no_clutch))

    def test_plot_top_clutch_scorers_valid(self):
        """
        Tests that plot_top_clutch_scorers returns a Figure when given a valid DataFrame.
        """
        fig = plot_top_clutch_scorers(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_top_clutch_scorers_all_nan(self):
        """
        Tests that plot_top_clutch_scorers returns None when all clutch goals are NaN.
        """
        df_nan = pd.DataFrame({
            "full_name": ["P1", "P2"],
            "clutch_goals": [float('nan'), float('nan')]
        })
        self.assertIsNone(plot_top_clutch_scorers(df_nan))


class TestTopImpactPlayers(BaseTestAnalytics):
    """
    Tests related to plot_top_impact_players().
    """

    def test_plot_top_impact_players_empty(self):
        """
        Tests that plot_top_impact_players returns None when given an empty DataFrame.
        """
        df_empty = pd.DataFrame()
        self.assertIsNone(plot_top_impact_players(df_empty))

        df_no_subbed = pd.DataFrame({"full_name": ["X"], "total_goals": [2]})
        self.assertIsNone(plot_top_impact_players(df_no_subbed))

    def test_plot_top_impact_players_valid(self):
        """
        Tests that plot_top_impact_players returns a Figure when given a valid DataFrame.
        """
        fig = plot_top_impact_players(self.sample_data, top_n=3)
        self.assertIsInstance(fig, Figure)

    def test_plot_top_impact_players_missing_subbed_on_goals(self):
        """
        Tests that plot_top_impact_players returns None when subbed_on_goals is missing.
        """
        df_missing = pd.DataFrame({"full_name": ["X"], "total_goals": [2]})
        self.assertIsNone(plot_top_impact_players(df_missing))


if __name__ == "__main__":
    unittest.main()
