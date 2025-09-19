"""
Test Suite for Team Analytics Module

This module contains unit tests for the team_analytics.py module. It ensures correctness of 
data processing,
filtering, and visualization logic. The tests focus on verifying logical correctness and 
exclude Streamlit UI elements.

Functions Tested:
- `test_process_match_data_loads_files()`: Ensures match data is loaded correctly.
- `test_process_match_data_team_colors()`: Checks if team colors are merged properly.
- `test_get_team_colors()`: Verifies retrieval of team colors for different teams.
- `test_get_team_colors_defaults()`: Ensures default colors are used when no data is available.
- `test_create_filters()`: Tests the filtering logic for different input cases.
- `test_create_filters_empty_df()`: Ensures proper handling when no data is available.
- `test_validate_data_existing_team()`: Tests data validation when a team exists.
- `test_validate_data_missing_team()`: Ensures a user message is displayed when a team is missing.
- `test_validate_data_missing_years()`: Checks if a user message appears when no years are 
    available.
- `test_validate_data_two_teams_one_missing()`: Validates behavior when one of two teams is 
    missing.
- `test_team_performance_pie_single_team()`: Tests team performance pie chart for a single team.
- `test_team_performance_pie_two_teams()`: Ensures proper chart generation when comparing two teams.
- `test_goal_distribution_by_year_type()`: Validates goal distribution visualization.
- `test_goal_distribution_brazil()`: Checks goal distribution visualization for Brazil.
- `test_plot_wc_comparison_france()`: Tests World Cup score distribution plots for France.
- `test_plot_wc_comparison_brazil()`: Ensures World Cup score distribution plots for Brazil.
- `test_world_cup_win_percentage_map()`: Verifies the World Cup win percentage map generation.
- `test_plot_all_teams_summary()`: Checks the summary visualization of top goal-scoring teams.
- `test_all_teams_selection()`: Ensures correct behavior when selecting "All Teams."
- `test_specific_team_selection()`: Validates correct filtering and visualization for 
    specific teams.

"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import plotly.graph_objects as go
from world_cup_26_predictions.team_analytics.team_analytics_tab import (
    process_match_data,
    get_team_colors,
    create_filters,
    validate_data,
    team_performance_pie,
    goal_distribution_by_year_type_side_by_side,
    plot_wc_comparison,
    world_cup_win_percentage_map,
    plot_all_teams_summary,
    run_team_analytics_tab,
    show_fun_facts,
)


# pylint: disable=too-many-public-methods
# disabling because more than 20 tests in TestTeamAnalytics
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

    @patch("team_analytics.team_analytics_tab.process_match_data")
    @patch(
        "team_analytics.team_analytics_tab.create_filters",
        return_value=("All Teams", None, None, None),
    )
    @patch("team_analytics.team_analytics_tab.display_chart")
    @patch("team_analytics.team_analytics_tab.show_fun_facts")
    def test_all_teams_selection(
        self, mock_fun_facts, mock_display_chart, _mock_create_filters, mock_process
    ):
        """Test that selecting 'All Teams' displays global statistics and charts."""
        mock_process.return_value = (self.matches_df, None)  # Use a real DataFrame

        run_team_analytics_tab()

        # Ensure charts are displayed twice (Win % Map + Top Goal-Scoring Teams)
        self.assertEqual(mock_display_chart.call_count, 2)
        mock_fun_facts.assert_called_once()

    @patch(
        "team_analytics.team_analytics_tab.process_match_data",
        return_value=(MagicMock(), None),
    )
    @patch(
        "team_analytics.team_analytics_tab.create_filters",
        return_value=("Brazil", "Germany", "Men", 1950),
    )
    @patch("team_analytics.team_analytics_tab.validate_data")
    @patch(
        "team_analytics.team_analytics_tab.goal_distribution_by_year_type_side_by_side"
    )
    @patch("team_analytics.team_analytics_tab.plot_wc_comparison")
    @patch("team_analytics.team_analytics_tab.display_chart")
    @patch("team_analytics.team_analytics_tab.team_performance_pie")
    def test_specific_team_selection(
        self,
        mock_performance_pie,
        mock_display_chart,
        _mock_wc_comparison,
        _mock_goal_dist,
        mock_validate,
        _mock_create_filters,
        _mock_process,
    ):
        """Test that selecting a specific team validates data and displays team-specific charts."""
        mock_validate.return_value = self.matches_df

        run_team_analytics_tab()

        self.assertEqual(mock_display_chart.call_count, 2)
        mock_performance_pie.assert_called_once()

    ##increasing test coverage

    @patch("streamlit.warning")
    def test_validate_data_no_matches(self, mock_warning):
        """Test validate data when non existenet team is filtered"""
        filtered_df = validate_data(self.matches_df, "Nonexistent Team")
        self.assertIsNone(filtered_df)
        mock_warning.assert_called_once()

    def test_create_filters_gender_filtering(self):
        """Test filtering logic based on gender selection."""
        matches_df = pd.DataFrame({"year": [1930, 1991, 1994, 2002, 2022]})

        with patch(
            "streamlit.radio", side_effect=["Men", "Women", "All"]
        ) as _mock_radio:
            _, _, selected_gender_men, _ = create_filters(matches_df)
            _, _, selected_gender_women, _ = create_filters(matches_df)
            _, _, selected_gender_all, _ = create_filters(matches_df)

        self.assertEqual(selected_gender_men, "Men")
        self.assertEqual(selected_gender_women, "Women")
        self.assertEqual(selected_gender_all, "All")

    def test_validate_data_missing_years_exists(self):
        """Test if validate_data correctly identifies missing World Cup years."""
        with patch("streamlit.info") as mock_info:
            validate_data(self.matches_df, "France", gender="Men")

            mock_info.assert_called()

    def test_validate_data_no_data_found(self):
        """Test when no data is found for a selected team and year."""
        matches_df = pd.DataFrame(columns=["home_team_name", "away_team_name", "year"])
        with patch("streamlit.warning") as mock_warning:
            validate_data(matches_df, "Argentina", gender="Men", year=1950)
            mock_warning.assert_called()

    def test_plot_wc_comparison_no_data(self):
        """Test plot_wc_comparison when no match data exists."""
        matches_df = pd.DataFrame(columns=["home_team_name", "away_team_name", "year"])
        with patch("streamlit.warning") as mock_warning:
            fig = plot_wc_comparison(matches_df, "Brazil", "Men")
            self.assertIsNone(fig)
            mock_warning.assert_called()

    def test_world_cup_win_percentage_map_round_2(self):
        """Test that world_cup_win_percentage_map executes without error and returns a figure."""
        fig = world_cup_win_percentage_map(self.matches_df)
        self.assertIsNotNone(fig)
        self.assertIsInstance(fig, go.Figure)

    def test_show_fun_facts(self):
        """Test that show_fun_facts runs correctly."""
        with patch("streamlit.markdown") as mock_markdown:
            show_fun_facts()
            mock_markdown.assert_called()

    def test_process_match_data_empty(self):
        """Test that process_match_data returns empty DataFrames when files are missing."""
        with patch("pandas.read_csv"):
            matches_df, teams_df = process_match_data()

            self.assertTrue(matches_df.empty)
            self.assertTrue(teams_df.empty)

    def test_get_team_colors_defaults_nonexistent_team(self):
        """Test get_team_colors when team does not exist."""
        colors = get_team_colors("NonExistentTeam", self.matches_df)

        self.assertEqual(colors["primary"], "blue")
        self.assertEqual(colors["secondary"], "red")
        self.assertEqual(colors["tertiary"], "gray")

    def test_create_filters_gender_years(self):
        """Test that gender selection correctly filters years."""
        _, _, gender, year = create_filters(self.matches_df)

        self.assertIn(gender, ["All", "Men", "Women"])
        self.assertTrue(isinstance(year, (str, int)))

    @patch("streamlit.info")
    def test_validate_data_missing_tournament_years(self, mock_info):
        """Test validate_data when a team is missing from some tournaments."""
        validate_data(self.matches_df, "France", gender="Men")

        mock_info.assert_called()

    @patch("streamlit.warning")
    def test_validate_data_no_data(self, mock_warning):
        """Test validate_data when no matches are found."""
        result = validate_data(self.matches_df, "NonExistentTeam", gender="Men")

        self.assertIsNone(result)
        mock_warning.assert_called()

    def test_plot_wc_comparison_no_data_exists(self):
        """Test plot_wc_comparison when a team has no matches."""
        fig = plot_wc_comparison(self.matches_df, "NonExistentTeam", "Men")

        self.assertIsNone(fig)

    @patch("streamlit.warning")
    def test_validate_data_team_missing_but_team2_exists(self, mock_warning):
        """Test validate_data when the first team has no data but team_2 does."""
        filtered_df = validate_data(
            self.matches_df, "Unknown Team", "Brazil", gender="Men"
        )

        mock_warning.assert_called_with(
            "No match data found for Unknown Team in the selected category: "
            "Men, Year: All Years. Showing only Brazil."
        )

        self.assertIsNotNone(filtered_df)
        self.assertIn("Brazil", filtered_df["home_team_name"].values)

    @patch("streamlit.warning")
    def test_validate_data_team2_missing_but_team1_exists(self, mock_warning):
        """Test validate_data when the second team has no data but team_1 does."""
        filtered_df = validate_data(
            self.matches_df, "France", "Unknown Team", gender="Men"
        )

        mock_warning.assert_called_with(
            "No match data found for Unknown Team in the selected category: "
            "Men, Year: All Years. Showing only France."
        )

        self.assertIsNotNone(filtered_df)
        self.assertIn("France", filtered_df["home_team_name"].values)

    def test_plot_wc_comparison_two_countries(self):
        """Test plot_wc_comparison when two valid countries are provided."""
        fig = plot_wc_comparison(self.matches_df, "France", "Men", "Brazil")

        self.assertIsNotNone(fig)

        country_data = self.matches_df[
            (self.matches_df["home_team_name"] == "France")
            | (self.matches_df["away_team_name"] == "France")
        ]
        country_data_2 = self.matches_df[
            (self.matches_df["home_team_name"] == "Brazil")
            | (self.matches_df["away_team_name"] == "Brazil")
        ]

        self.assertFalse(country_data.empty)
        self.assertFalse(country_data_2.empty)
        self.assertGreater(
            country_data["home_team_score"].sum()
            + country_data["away_team_score"].sum(),
            0,
        )
        self.assertGreater(
            country_data_2["home_team_score"].sum()
            + country_data_2["away_team_score"].sum(),
            0,
        )

        team_colors_2 = get_team_colors("Brazil", self.matches_df)
        self.assertIn("primary", team_colors_2)

    def test_goal_distribution_with_two_teams(self):
        """Test goal distribution when comparing two teams."""
        fig = goal_distribution_by_year_type_side_by_side(
            self.matches_df, "France", "Brazil", "All Years", "Men"
        )

        self.assertIsNotNone(fig)

        team_colors_2 = get_team_colors("Brazil", self.matches_df)
        self.assertIn("primary", team_colors_2)
        self.assertIsInstance(team_colors_2["primary"], str)

        for trace in fig.data:
            self.assertEqual(len(trace.x), len(trace.y))

        france_goals = [trace.y for trace in fig.data if trace.name == "France"]
        brazil_goals = [trace.y for trace in fig.data if trace.name == "Brazil"]

        self.assertTrue(any(val > 0 for val in france_goals[0]))
        self.assertTrue(any(val > 0 for val in brazil_goals[0]))


if __name__ == "__main__":
    unittest.main()
