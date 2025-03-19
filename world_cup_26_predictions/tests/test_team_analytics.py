"""
Test Suite for Team Analytics Module

This module contains unit tests for the team_analytics.py module. It ensures correctness of 
data processing,
filtering, and visualization logic. The tests focus on verifying logical correctness and 
exclude Streamlit UI elements.

Functions Tested:
- test_get_team_colors(): Tests retrieving team colors for different teams.
- test_validate_data(): Tests data validation logic for different scenarios.
- test_create_filters(): Tests filtering logic for different inputs.
- test_team_performance_pie(): Tests team performance visualization.
- test_goal_distribution_by_year_type(): Tests goal distribution visualization.
- test_plot_wc_comparison(): Tests World Cup score distribution plots.
- test_world_cup_win_percentage_map(): Tests World Cup win percentage map.
- test_plot_all_teams_summary(): Tests plotting top goal-scoring teams.

"""

import unittest
from unittest.mock import patch
import pandas as pd
from team_analytics.team_analytics_tab import (
    process_match_data,
    get_team_colors,
    create_filters,
    validate_data,
    team_performance_pie,
    goal_distribution_by_year_type_side_by_side,
    plot_wc_comparison,
    world_cup_win_percentage_map,
    plot_all_teams_summary,
)


class TestTeamAnalytics(unittest.TestCase):
    """Unit tests for team_analytics module."""

    def setUp(self):
        """Set up a sample dataset for testing."""
        data = {
            "team_1": ["France", "United States", "Yugoslavia", "Brazil"],
            "team_2": ["Mexico", "Belgium", "Brazil", "Germany"],
            "year": [1930, 1930, 1930, 1950],
            "home_team_name": ["France", "United States", "Yugoslavia", "Brazil"],
            "away_team_name": ["Mexico", "Belgium", "Brazil", "Germany"],
            "home_team_score": [4, 3, 2, 1],
            "away_team_score": [1, 0, 1, 0],
            "home_team_win": [1, 1, 1, 1],
            "away_team_win": [0, 0, 0, 0],
            "draw": [0, 0, 0, 0],
            "team_1_color_1": ["Blue", "Red", "Blue", "Green"],
            "team_1_color_2": ["White", "White", "White", "Yellow"],
            "team_1_color_3": ["Red", "Blue", "Red", "Blue"],
            "team_2_color_1": ["Green", "Black", "Green", "Black"],
            "team_2_color_2": ["White", "Yellow", "Yellow", "Red"],
            "team_2_color_3": ["Red", "Red", "Blue", "Yellow"],
        }
        self.matches_df = pd.DataFrame(data)

    # data loading
    @patch("pandas.read_csv")
    def test_process_match_data_loads_files(self, mock_read_csv):
        """Test that process_match_data loads match data correctly."""
        mock_read_csv.return_value = pd.DataFrame(
            {"match_name": ["France vs Mexico"], "tournament_id": ["WC-1930"]}
        )

        matches_df, teams_df = process_match_data()

        self.assertFalse(matches_df.empty)
        self.assertIn("team_1", matches_df.columns)
        self.assertIn("team_2", matches_df.columns)
        self.assertIn("year", matches_df.columns)
        self.assertEqual(matches_df.loc[0, "team_1"], "France")
        self.assertEqual(matches_df.loc[0, "team_2"], "Mexico")
        self.assertIsInstance(teams_df, pd.DataFrame)

    @patch("pandas.read_csv")
    def test_process_match_data_team_colors(self, mock_read_csv):
        """Test that process_match_data correctly merges team colors."""
        mock_read_csv.side_effect = lambda x: (
            pd.DataFrame(
                {"match_name": ["France vs Mexico"], "tournament_id": ["WC-1930"]}
            )
            if "matches.csv" in x
            else pd.DataFrame()
        )

        matches_df, _ = process_match_data()

        self.assertIn("team_1_color_1", matches_df.columns)
        self.assertIn("team_2_color_1", matches_df.columns)
        self.assertEqual(matches_df.loc[0, "team_1_color_1"], "Blue")
        self.assertEqual(matches_df.loc[0, "team_2_color_1"], "Green")

    # when team colors exist vs not
    def test_get_team_colors(self):
        """Test retrieving team colors."""
        colors = get_team_colors("France", self.matches_df)
        self.assertEqual(colors["primary"], "Blue")
        self.assertEqual(colors["secondary"], "White")
        self.assertEqual(colors["tertiary"], "Red")

    def test_get_team_colors_defaults(self):
        """Test retrieving team colors for a team that doesnt exist/doesnt have colors."""
        colors_default = get_team_colors("Atlantis", self.matches_df)
        self.assertEqual(colors_default["primary"], "blue")
        self.assertEqual(colors_default["secondary"], "red")
        self.assertEqual(colors_default["tertiary"], "gray")

    def test_create_filters(self):
        """Test filtering logic for different inputs."""
        selected_team, selected_team_2 = create_filters(self.matches_df)[:2]
        selected_gender, selected_year = create_filters(self.matches_df)[2:]
        self.assertIsInstance(selected_team, str)
        self.assertIn(selected_gender, ["All", "Men", "Women"])

        if selected_team_2:
            self.assertIsInstance(selected_team_2, str)

        years = sorted(self.matches_df["year"].dropna().astype(int).unique().tolist())
        available_years = ["All Years"] + years
        self.assertIn(selected_year, available_years)

    def test_create_filters_empty_df(self):
        """Test create_filters when matches_df is empty."""
        empty_df = pd.DataFrame()
        selected_team, selected_team_2, selected_gender, selected_year = create_filters(
            empty_df
        )

        self.assertIsNone(selected_team)
        self.assertIsNone(selected_team_2)
        self.assertIsNone(selected_gender)
        self.assertIsNone(selected_year)

    ## test functionality of user message when data doesnt exist
    def test_validate_data_existing_team(self):
        """Test validate_data when the team exists in the dataset."""
        filtered_df = validate_data(self.matches_df, "France", gender="Men")
        self.assertIsNotNone(filtered_df)
        self.assertFalse(filtered_df.empty)
        self.assertIn(1930, filtered_df["year"].values)

    def test_validate_data_missing_team(self):
        """Test validate_data when the team is missing, ensuring a message to user is displayed."""
        with patch("streamlit.info") as mock_info:
            validate_data(self.matches_df, "Germany", gender="Men")
            mock_info.assert_called()

    def test_validate_data_missing_years(self):
        """Test validate_data to check that a missing year message to user is displayed."""
        with patch("streamlit.info") as mock_info:
            validate_data(self.matches_df, "France", gender="Men")
            mock_info.assert_called()

    def test_validate_data_two_teams_one_missing(self):
        """Test validate_data when comparing two teams and one is missing,
        ensuring a message is displayed."""
        with patch("streamlit.info") as mock_info:
            validate_data(self.matches_df, "France", "Germany", gender="Men")
            mock_info.assert_called()

    # figure testing
    @patch("streamlit.plotly_chart")
    def test_team_performance_pie_single_team(self, mock_plotly_chart):
        """Test performance pie chart for a single team (France)."""
        team_performance_pie("France", None, self.matches_df, "Men", "All Years")

        mock_plotly_chart.assert_called()

    @patch("streamlit.plotly_chart")
    def test_team_performance_pie_two_teams(self, mock_plotly_chart):
        """Test performance pie chart for two teams (France vs Brazil)."""
        team_performance_pie("France", "Brazil", self.matches_df, "Men", "All Years")

        self.assertEqual(mock_plotly_chart.call_count, 2)

    def test_goal_distribution_by_year_type(self):
        """Test goal distribution visualization function."""
        fig = goal_distribution_by_year_type_side_by_side(
            self.matches_df, "France", None, "All Years", "Men"
        )
        self.assertEqual(fig.data[0].name, "France")
        self.assertGreater(len(fig.data), 0)

    def test_goal_distribution_brazil(self):
        """Test goal distribution visualization for Brazil."""
        fig_2 = goal_distribution_by_year_type_side_by_side(
            self.matches_df, "Brazil", None, "All Years", "Men"
        )
        self.assertGreater(len(fig_2.data), 0)
        self.assertIn("Brazil", [trace.name for trace in fig_2.data])

    def test_plot_wc_comparison_france(self):
        """Test World Cup score distribution plot for France."""
        fig = plot_wc_comparison(self.matches_df, "France", "Men")
        self.assertGreater(len(fig.data), 0)

    def test_plot_wc_comparison_brazil(self):
        """Test World Cup score distribution plot for Brazil."""
        fig_2 = plot_wc_comparison(self.matches_df, "Brazil", "Men")
        self.assertGreater(len(fig_2.data), 0)

    def test_world_cup_win_percentage_map(self):
        """Test World Cup win percentage map generation."""
        fig = world_cup_win_percentage_map(self.matches_df)
        self.assertGreater(len(fig.data), 0)

    def test_plot_all_teams_summary(self):
        """Test plotting top goal-scoring teams."""
        fig = plot_all_teams_summary(self.matches_df)
        self.assertGreater(len(fig.data), 0)


if __name__ == "__main__":
    unittest.main()
