"""
Team Analytics Module

This module provides functions and visualizations for analyzing World Cup data using Streamlit.
It includes data processing, filtering, performance comparison, goal distribution analysis, and 
interactive visualizations.

### Functions:
- **process_match_data()**: Loads and cleans match data, merging team color information.
- **get_team_colors(team, df)**: Retrieves a team's flag colors from the dataset.
- **create_filters(matches_df)**: Generates Streamlit UI filters for team, year, and gender 
selection.
- **validate_data(df, team, team_2, gender, year)**: Checks if the selected filters have 
valid data.
- **team_performance_pie(team_name, team_2, df, gender, selected_year)**: Creates pie charts 
for team performance.
- **goal_distribution_by_year_type_side_by_side(df, team, team_2, selected_year, 
selected_gender)**: 
  Displays goal distribution over the years for one or two teams.
- **plot_wc_comparison(df, country, gender, country_2)**: Generates a violin plot of score 
distributions.
- **world_cup_win_percentage_map(matches_df)**: Creates a world map showing World Cup win 
percentages.
- **plot_all_teams_summary(df)**: Displays top goal-scoring teams in a bar chart.
- **show_fun_facts()**: Displays interesting World Cup trivia facts.
- **display_trivia_section()**: Renders a trivia section for the Men's and Women's World Cups.
- **display_chart(fig)**: Helper function for displaying Plotly charts with a consistent 
layout.
- **run_team_analytics_tab()**: Main function to execute the Streamlit analytics tab.

### Usage:
Imports to pages\analysis_tool.py for use in streamlit app.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

pd.options.mode.chained_assignment = None


## data processing, color helper function, create filters for streamlit
def process_match_data():
    """
    Functionality: Gets data from data folder, merges in flag information, returns clean dfs
    Arguments: None
    Return Values: dataframes, namely matches_df which is df to be worked with primarily
    Exceptions: none
    """
    filenames = [
        "award_winners.csv",
        "host_countries.csv",
        "players.csv",
        "substitutions.csv",
        "awards.csv",
        "manager_appearances.csv",
        "qualified_teams.csv",
        "team_appearances.csv",
        "bookings.csv",
        "manager_appointments.csv",
        "referee_appearances.csv",
        "teams.csv",
        "confederations.csv",
        "managers.csv",
        "referee_appointments.csv",
        "tournament_stages.csv",
        "goals.csv",
        "matches.csv",
        "referees.csv",
        "tournament_standings.csv",
        "group_standings.csv",
        "penalty_kicks.csv",
        "squads.csv",
        "tournaments.csv",
        "groups.csv",
        "player_appearances.csv",
        "stadiums.csv",
    ]

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    dfs = {}
    for file_name in filenames:
        name = os.path.splitext(file_name)[0]
        full_path = os.path.join(base_path, file_name)

        if os.path.exists(full_path):
            dfs[name] = pd.read_csv(full_path)
        else:
            print(f"Warning: {file_name} not found in {base_path}")
            dfs[name] = pd.DataFrame()

    matches_df = dfs.get("matches", pd.DataFrame())
    teams_df = dfs.get("teams", pd.DataFrame())

    if not matches_df.empty:
        matches_df[["team_1", "team_2"]] = matches_df["match_name"].str.split(
            " vs ", expand=True
        )
        matches_df["year"] = matches_df["tournament_id"].str.extract(r"(\d{4})")
        matches_df["year"] = pd.to_numeric(matches_df["year"], errors="coerce")

    df_flags = pd.DataFrame(
        [
            ("France", "Blue", "White", "Red"),
            ("United States", "Red", "White", "Blue"),
            ("Yugoslavia", "Blue", "White", "Red"),
            ("Romania", "Blue", "Yellow", "Red"),
            ("Argentina", "Light Blue", "White", "Gold"),
            ("Chile", "Red", "White", "Blue"),
            ("Uruguay", "Blue", "White", "Yellow"),
            ("Brazil", "Green", "Yellow", "Blue"),
            ("Paraguay", "Red", "White", "Blue"),
            ("Austria", "Red", "White", "Red"),
            ("Czechoslovakia", "Blue", "White", "Red"),
            ("Germany", "Black", "Red", "Yellow"),
            ("Hungary", "Red", "White", "Green"),
            ("Italy", "Green", "White", "Red"),
            ("Spain", "Red", "Yellow", "Red"),
            ("Sweden", "Blue", "Yellow", "Blue"),
            ("Switzerland", "Red", "White", "Red"),
            ("Cuba", "Red", "White", "Blue"),
            ("England", "White", "Red", "White"),
            ("West Germany", "Black", "Red", "Yellow"),
            ("Turkey", "Red", "White", "Red"),
            ("Northern Ireland", "White", "Red", "White"),
            ("Soviet Union", "Red", "Yellow", "Red"),
            ("Mexico", "Green", "White", "Red"),
            ("Wales", "Red", "White", "Green"),
            ("Portugal", "Green", "Red", "Yellow"),
            ("North Korea", "Red", "White", "Blue"),
            ("Peru", "Red", "White", "Red"),
            ("Belgium", "Black", "Yellow", "Red"),
            ("Bulgaria", "White", "Green", "Red"),
            ("East Germany", "Black", "Red", "Yellow"),
            ("Zaire", "Green", "Yellow", "Red"),
            ("Poland", "White", "Red", "White"),
            ("Australia", "Blue", "White", "Red"),
            ("Scotland", "Blue", "White", "Blue"),
            ("Netherlands", "Red", "White", "Blue"),
            ("Haiti", "Blue", "Red", "White"),
            ("Tunisia", "Red", "White", "Red"),
            ("Algeria", "Green", "White", "Red"),
            ("Honduras", "Blue", "White", "Blue"),
            ("Canada", "Red", "White", "Red"),
            ("Morocco", "Red", "Green", "Red"),
            ("South Korea", "White", "Black", "Red"),
            ("Iraq", "Red", "White", "Black"),
            ("Denmark", "Red", "White", "Red"),
            ("United Arab Emirates", "Red", "Green", "Black"),
            ("Costa Rica", "Red", "White", "Blue"),
            ("Cameroon", "Green", "Red", "Yellow"),
            ("Republic of Ireland", "Green", "White", "Orange"),
            ("China", "Red", "Yellow", "Red"),
            ("Japan", "White", "Red", "White"),
            ("Chinese Taipei", "Blue", "White", "Red"),
            ("Norway", "Red", "White", "Blue"),
            ("Colombia", "Yellow", "Blue", "Red"),
            ("Nigeria", "Green", "White", "Green"),
            ("Saudi Arabia", "Green", "White", "Green"),
            ("Bolivia", "Red", "Yellow", "Green"),
            ("Russia", "White", "Blue", "Red"),
            ("Greece", "Blue", "White", "Blue"),
            ("Jamaica", "Black", "Yellow", "Green"),
            ("South Africa", "Green", "Yellow", "Black"),
            ("Ghana", "Red", "Yellow", "Green"),
            ("Croatia", "Red", "White", "Blue"),
            ("Senegal", "Green", "Yellow", "Red"),
            ("Slovenia", "White", "Blue", "Red"),
            ("Ecuador", "Yellow", "Blue", "Red"),
            ("Trinidad and Tobago", "Red", "White", "Black"),
            ("Serbia and Montenegro", "Red", "Blue", "White"),
            ("Angola", "Red", "Black", "Yellow"),
            ("Czech Republic", "White", "Red", "Blue"),
            ("Togo", "Green", "Yellow", "Red"),
            ("Iran", "Green", "White", "Red"),
            ("Ivory Coast", "Orange", "White", "Green"),
            ("Ukraine", "Blue", "Yellow", "Blue"),
            ("New Zealand", "Blue", "Red", "White"),
            ("Serbia", "Red", "Blue", "White"),
            ("Slovakia", "White", "Blue", "Red"),
            ("Equatorial Guinea", "Blue", "White", "Green"),
            ("Bosnia and Herzegovina", "Blue", "Yellow", "White"),
            ("Thailand", "Red", "White", "Blue"),
            ("Egypt", "Red", "White", "Black"),
            ("Iceland", "Blue", "White", "Red"),
            ("Panama", "Red", "White", "Blue"),
            ("Qatar", "Maroon", "White", "Maroon"),
        ],
        columns=["team", "team_color_1", "team_color_2", "team_color_3"],
    )

    matches_df = matches_df.merge(
        df_flags, left_on="team_1", right_on="team", how="left"
    )
    matches_df.rename(
        columns={
            "team_color_1": "team_1_color_1",
            "team_color_2": "team_1_color_2",
            "team_color_3": "team_1_color_3",
        },
        inplace=True,
    )
    matches_df.drop(columns=["team"], inplace=True)

    matches_df = matches_df.merge(
        df_flags, left_on="team_2", right_on="team", how="left"
    )
    matches_df.rename(
        columns={
            "team_color_1": "team_2_color_1",
            "team_color_2": "team_2_color_2",
            "team_color_3": "team_2_color_3",
        },
        inplace=True,
    )
    matches_df.drop(columns=["team"], inplace=True)

    return matches_df, teams_df


def get_team_colors(team, df):
    """
    Functionality: gets team colors
    Arguments: team name and df
    Return Values: country flag colors
    Exceptions: none
    """
    if team in df["team_1"].values:
        team_row = df.loc[df["team_1"] == team].iloc[0]
        prefix = "team_1"
    elif team in df["team_2"].values:
        team_row = df.loc[df["team_2"] == team].iloc[0]
        prefix = "team_2"
    else:
        return {
            "primary": "blue",
            "secondary": "red",
            "tertiary": "gray",
        }

    return {
        "primary": team_row.get(f"{prefix}_color_1", "blue"),
        "secondary": team_row.get(f"{prefix}_color_2", "red"),
        "tertiary": team_row.get(f"{prefix}_color_3", "gray"),
    }


def create_filters(matches_df):
    """
    Functionality: Creates filters for UI based on df options
    Arguments: dataframe of interest, matches_df
    Return Values: selected values
    Exceptions: none
    """
    if matches_df.empty:
        st.error("The matches data is empty.")
        return None, None, None, None

    if "team_1" in matches_df.columns and "team_2" in matches_df.columns:
        team_1_set = set(matches_df["team_1"].dropna().astype(str))
        team_2_set = set(matches_df["team_2"].dropna().astype(str))
        teams = ["All Teams"] + sorted(team_1_set.union(team_2_set))
    else:
        st.error("Missing team data in the DataFrame.")
        teams = []

    with st.expander("Select Filters", expanded=True):
        st.subheader("Filters")

        selected_team = st.selectbox("Select Team:", teams)

        second_team_options = (
            ["None"] + teams if selected_team != "All Teams" else ["None"]
        )
        selected_team_2 = st.selectbox(
            "Compare with Another Team (Optional):", second_team_options, index=0
        )
        selected_team_2 = None if selected_team_2 == "None" else selected_team_2

        selected_gender = st.radio("Select Gender:", ["All", "Men", "Women"])

        years = sorted(matches_df["year"].dropna().astype(int).unique())
        filtered_years = years

        if selected_gender == "Men":
            filtered_years = [y for y in years if y % 2 == 0]
        elif selected_gender == "Women":
            filtered_years = [y for y in years if y % 2 != 0]

        filtered_years.insert(0, "All Years")
        selected_year = st.selectbox("Select Year:", filtered_years)

    return selected_team, selected_team_2, selected_gender, selected_year


def validate_data(df, team, team_2=None, gender="All", year="All Years"):
    """
    Functionality: Checks if the given filters have valid data in the DataFrame and
    lists missing years.
    Arguments: df (DataFrame), team (str), team_2 (str or None), gender (str), year
    (str or int)
    Returns: Filtered DataFrame (or None if no valid data is found)
    """

    mens_wc_years = list(range(1930, 2026, 4))
    womens_wc_years = list(range(1991, 2026, 4))

    if gender == "Men":
        df = df[df["year"] % 2 == 0]
    if gender == "Women":
        df = df[df["year"] % 2 != 0]

    if year != "All Years":
        df = df[df["year"] == int(year)]

    team_wc_years = set(
        df[(df["home_team_name"] == team) | (df["away_team_name"] == team)]["year"]
    )
    team_missing_men = sorted(set(mens_wc_years) - team_wc_years)
    team_missing_women = sorted(set(womens_wc_years) - team_wc_years)
    team_2_missing_men, team_2_missing_women = [], []

    if team_2:
        team_2_wc_years = set(
            df[(df["home_team_name"] == team_2) | (df["away_team_name"] == team_2)][
                "year"
            ]
        )

        team_2_missing_men = sorted(set(mens_wc_years) - team_2_wc_years)
        team_2_missing_women = sorted(set(womens_wc_years) - team_2_wc_years)

    # notate if missing data so user knows not error
    if gender in ["Men", "All"] and team_missing_men:
        st.info(
            f"⚠️ **{team} (Men) did not appear in the World Cup in:** "
            f"{', '.join(map(str, team_missing_men))}"
        )

    if gender in ["Women", "All"] and team_missing_women:
        st.info(
            f"⚠️ **{team} (Women) did not appear in the World Cup in:** "
            f"{', '.join(map(str, team_missing_women))}"
        )

    if team_2:
        if gender in ["Men", "All"] and team_2_missing_men:
            st.info(
                f"⚠️ **{team_2} (Men) did not appear in the World Cup in:** "
                f"{', '.join(map(str, team_2_missing_men))}"
            )

        if gender in ["Women", "All"] and team_2_missing_women:
            st.info(
                f"⚠️ **{team_2} (Women) did not appear in the World Cup in:** "
                f"{', '.join(map(str, team_2_missing_women))}"
            )

    # missing data case
    team_data = df[(df["home_team_name"] == team) | (df["away_team_name"] == team)]

    team_data_2 = (
        df[(df["home_team_name"] == team_2) | (df["away_team_name"] == team_2)]
        if team_2
        else None
    )

    if team_data.empty and (not team_2 or team_data_2 is None or team_data_2.empty):
        st.warning(
            f"No match data found for {team} (or {team_2}) in the selected "
            f"category: {gender}, Year: {year}."
        )
        return None
    if team_data.empty:
        st.warning(
            f"No match data found for {team} in the selected category: {gender}, "
            f"Year: {year}. Showing only {team_2}."
        )
        return team_data_2
    if team_2 and team_data_2 is not None and team_data_2.empty:
        st.warning(
            f"No match data found for {team_2} in the selected category: {gender}, "
            f"Year: {year}. Showing only {team}."
        )
        return team_data

    return df


## Page when looking at statistics for one team or comparing two teams
def team_performance_pie(team_name, team_2, df, gender, selected_year):
    """
    Functionality: Creates pie chart comparing performance between teams
    Arguments: team name(s) of interest, data frame with info, gender, year
    Return Values: pie chart of selected information
    Exceptions: none
    """
    if gender == "Men":
        df = df[df["year"] % 2 == 0]
    elif gender == "Women":
        df = df[df["year"] % 2 != 0]

    if selected_year != "All Years":
        df = df[df["year"] == selected_year]

    def get_performance_data(team):
        home_matches = df[df["home_team_name"] == team]
        away_matches = df[df["away_team_name"] == team]

        home_wins = home_matches["home_team_win"].sum()
        away_wins = away_matches["away_team_win"].sum()
        home_draws = home_matches["draw"].sum()
        away_draws = away_matches["draw"].sum()

        home_losses = len(home_matches) - home_wins - home_draws
        away_losses = len(away_matches) - away_wins - away_draws

        return pd.DataFrame(
            {
                "Result": ["Win", "Loss", "Draw"],
                "Count": [
                    home_wins + away_wins,
                    home_losses + away_losses,
                    home_draws + away_draws,
                ],
            }
        )

    col1, col2 = st.columns(2) if team_2 else (st.container(), None)

    with col1:
        data = get_performance_data(team_name)
        fig = px.pie(
            data, names="Result", values="Count", title=f"Performance of {team_name}"
        )
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#E0E0E0",
            plot_bgcolor="#E0E0E0",
            font={"color": "black"},
            xaxis={"showgrid": False, "color": "black"},
            yaxis={"showgrid": True, "gridcolor": "gray", "color": "black"},
            title_font={"color": "black"},
            legend={"font": {"color": "black"}},
        )
        st.plotly_chart(fig, use_container_width=True)

    if team_2:
        with col2:
            data_2 = get_performance_data(team_2)
            fig_2 = px.pie(
                data_2, names="Result", values="Count", title=f"Performance of {team_2}"
            )
            fig_2.update_layout(
                template="plotly_white",
                paper_bgcolor="#E0E0E0",
                plot_bgcolor="#E0E0E0",
                font={"color": "black"},
                xaxis={"showgrid": False, "color": "black"},
                yaxis={"showgrid": True, "gridcolor": "gray", "color": "black"},
                title_font={"color": "black"},
                legend={"font": {"color": "black"}},
            )
            st.plotly_chart(fig_2, use_container_width=True)


def goal_distribution_by_year_type_side_by_side(
    df, team, team_2, selected_year, selected_gender
):
    """
    Functionality: Bar chart comparing goal distribution for one/two teams with gender filtering
    Arguments: team name(s) of interest, data frame with info, years and gender of interest
    Return Values: colors of team
    Exceptions: none
    """

    if selected_gender == "Men":
        df = df[df["year"] % 2 == 0]
    elif selected_gender == "Women":
        df = df[df["year"] % 2 != 0]

    team_data = df[(df["team_1"] == team) | (df["team_2"] == team)]
    team_data_2 = (
        df[(df["team_1"] == team_2) | (df["team_2"] == team_2)] if team_2 else None
    )

    if selected_year != "All Years":
        team_data = team_data[team_data["year"] == selected_year]
        if team_data_2 is not None:
            team_data_2 = team_data_2[team_data_2["year"] == selected_year]

    team_colors = get_team_colors(team, df)
    color_map = {team: team_colors["primary"]}

    team_data["goals"] = team_data.apply(
        lambda row: (
            row["home_team_score"] if row["team_1"] == team else row["away_team_score"]
        ),
        axis=1,
    )

    combined_data = team_data.groupby("year")["goals"].sum().reset_index()
    combined_data["Team"] = team

    # if second team to compare
    if team_2:
        team_colors_2 = get_team_colors(team_2, df)
        color_map[team_2] = team_colors_2["primary"]

        team_data_2["goals"] = team_data_2.apply(
            lambda r: (
                r["home_team_score"] if r["team_1"] == team_2 else r["away_team_score"]
            ),
            axis=1,
        )

        combined_data_2 = team_data_2.groupby("year")["goals"].sum().reset_index()
        combined_data_2["Team"] = team_2

        combined_data = pd.concat([combined_data, combined_data_2])

    # plot
    fig = px.bar(
        combined_data,
        x="year",
        y="goals",
        color="Team",
        title="Goal Distribution Over the Years",
        color_discrete_map=color_map,
        barmode="group",
    )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#E0E0E0",
        plot_bgcolor="#E0E0E0",
        font={"color": "black"},
        xaxis={"showgrid": False, "color": "black"},
        yaxis={"showgrid": True, "gridcolor": "gray", "color": "black"},
        title_font={"color": "black"},
        legend={"font": {"color": "black"}},
    )

    return fig


def plot_wc_comparison(df, country, gender, country_2=None):
    """
    Functionality: Creates a violin plot comparing score distributions with gender filtering.
    Arguments: team name of interest, matches_df, gender
    Return Values: plot
    Exceptions: none
    """

    if gender == "Men":
        df = df[df["year"] % 2 == 0]
    elif gender == "Women":
        df = df[df["year"] % 2 != 0]

    country_data = df[
        (df["home_team_name"] == country) | (df["away_team_name"] == country)
    ]

    country_data_2 = None
    if country_2:
        country_data_2 = df[
            (df["home_team_name"] == country_2) | (df["away_team_name"] == country_2)
        ]

    if country_data.empty:
        st.warning(
            f"No match data found for {country} in the selected gender category."
        )
        return None

    # assign World Cup type based on the year
    country_data.loc[:, "wc_type"] = country_data["year"].apply(
        lambda x: "Men's WC" if x % 2 == 0 else "Women's WC"
    )

    # create DataFrame for scores
    scores_df = pd.DataFrame(
        {
            "score": pd.concat(
                [country_data["home_team_score"], country_data["away_team_score"]]
            ),
            "team": [country] * (len(country_data) * 2),
            "wc_type": country_data["wc_type"].tolist() * 2,
        }
    )

    team_colors = get_team_colors(country, df)
    color_map = {
        country: team_colors["primary"] if pd.notna(team_colors["primary"]) else "blue"
    }

    if country_2 and country_data_2 is not None and not country_data_2.empty:
        country_data_2["wc_type"] = country_data_2["year"].apply(
            lambda x: "Men's WC" if x % 2 == 0 else "Women's WC"
        )

        scores_df_2 = pd.DataFrame(
            {
                "score": pd.concat(
                    [
                        country_data_2["home_team_score"],
                        country_data_2["away_team_score"],
                    ]
                ),
                "team": [country_2] * (len(country_data_2) * 2),
                "wc_type": country_data_2["wc_type"].tolist() * 2,
            }
        )

        scores_df = pd.concat([scores_df, scores_df_2], ignore_index=True)

        team_colors_2 = get_team_colors(country_2, df)
        color_map[country_2] = (
            team_colors_2.get("primary")
            if pd.notna(team_colors_2.get("primary"))
            else "green"
        )

    scores_df.loc[:, "team_color"] = scores_df["team"].map(color_map)
    scores_df.loc[:, "team_color"] = scores_df["team_color"].fillna("gray")

    if gender == "Men":
        scores_df = scores_df[scores_df["wc_type"] == "Men's WC"].copy()
    elif gender == "Women":
        scores_df = scores_df[scores_df["wc_type"] == "Women's WC"].copy()

    fig_violin = px.violin(
        scores_df,
        x="team",
        y="score",
        color="wc_type",
        title=f"{country} Match Score Distribution (Home vs Away)",
        labels={"team": "Team", "score": "Score", "wc_type": "World Cup Type"},
        color_discrete_map=color_map,
        category_orders={"team": [country] + ([country_2] if country_2 else [])},
    )

    fig_violin.update_layout(
        template="plotly_white",
        paper_bgcolor="#E0E0E0",
        plot_bgcolor="#E0E0E0",
        font={"color": "black"},
        xaxis={"showgrid": False, "color": "black"},
        yaxis={"showgrid": True, "gridcolor": "gray", "color": "black"},
        title_font={"color": "black"},
        legend={"font": {"color": "black"}},
    )

    return fig_violin


## Page when all teams are selected
def world_cup_win_percentage_map(matches_df):
    """
    Functionality: Creates world cup win percentage map
    Arguments: matches_df
    Return Values: world map with win percentages
    Exceptions: none
    """

    country_stats = {}

    for _, row in matches_df.iterrows():
        home_team = row["home_team_name"]
        away_team = row["away_team_name"]
        home_win = row["home_team_win"]
        away_win = row["away_team_win"]

        if home_team not in country_stats:
            country_stats[home_team] = {"wins": 0, "games": 0}
        if away_team not in country_stats:
            country_stats[away_team] = {"wins": 0, "games": 0}

        country_stats[home_team]["games"] += 1
        country_stats[away_team]["games"] += 1

        if home_win == 1:
            country_stats[home_team]["wins"] += 1
        elif away_win == 1:
            country_stats[away_team]["wins"] += 1

    country_data = []
    for country, stats in country_stats.items():
        win_percentage = (
            (stats["wins"] / stats["games"]) * 100 if stats["games"] > 0 else 0
        )
        country_data.append({"country": country, "win_percentage": win_percentage})

    df = pd.DataFrame(country_data)

    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="win_percentage",
        color_continuous_scale="Viridis",
        title="🌍 World Cup Team Win Percentages",
        labels={"win_percentage": "Win %"},
        projection="natural earth",
    )

    fig.update_layout(
        geo={"showcoastlines": True, "showland": True, "landcolor": "lightgray"},
        coloraxis_colorbar={"title": "Win %"},
    )

    return fig


##helper funcs to reduce local vars
def plot_all_teams_summary(df):
    """
    Functionality: Plots teams with most wins
    Arguments: matches_df
    Return Values: plot returned
    """
    # combine home and away team goals
    team_goals = (
        df.melt(
            id_vars=["home_team_score", "away_team_score"],
            value_vars=["home_team_name", "away_team_name"],
            var_name="location",
            value_name="team",
        )
        .assign(
            goals=lambda x: x.apply(
                lambda row: (
                    row["home_team_score"]
                    if row["location"] == "home_team_name"
                    else row["away_team_score"]
                ),
                axis=1,
            )
        )
        .groupby("team", as_index=False)["goals"]
        .sum()
    )

    top_teams = team_goals.sort_values(by="goals", ascending=False).head(15)

    fig = px.bar(
        top_teams,
        x="team",
        y="goals",
        title="Top 15 Goal-Scoring Teams in World Cup History",
        labels={"team": "Team", "goals": "Goals Scored"},
        color_discrete_sequence=["gold"],
    )

    return fig


def show_fun_facts():
    """
    Functionality: Displays world cup fun facts
    Arguments: none
    Return Values: none
    Exceptions: none
    """
    st.subheader("World Cup Facts")

    fun_facts = [
        "🏆 Brazil has won the most World Cups (5).",
        "🎯 The fastest goal in World Cup history was scored in 11 seconds!",
        "🚀 Germany has the most goals scored in World Cup history.",
        "🌎 The 2026 World Cup will be hosted by 3 countries: USA, Canada, and Mexico.",
        "⚽ The 1950 World Cup was the only one without a final match!",
    ]

    for fact in fun_facts:
        st.markdown(f"✅ {fact}")


def display_trivia_section():
    """Displays the trivia section for Men's & Women's World Cups."""
    st.markdown("---")
    st.subheader("Men & Women World Cup Trivia")

    trivia_data = {
        "Men's World Cup": [
            ("🏟️ First Edition", "1930"),
            ("🗓️ Total Tournaments", "22"),
            ("🏆 Most Titles", "Brazil (5)"),
            ("👑 Current Champion", "Argentina (2022)"),
        ],
        "Women's World Cup": [
            ("🏟️ First Edition", "1991"),
            ("🗓️ Total Tournaments", "9"),
            ("🏆 Most Titles", "USA (4)"),
            ("👑 Current Champion", "Spain (2023)"),
        ],
    }

    for section, metrics in trivia_data.items():
        st.subheader(section)
        cols = st.columns(4)
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.metric(label, value)

    st.markdown("---")


def display_chart(fig):
    """Helper function to display Plotly charts with consistent settings."""
    if fig:
        st.plotly_chart(fig, use_container_width=True)


##run app
def run_team_analytics_tab():
    """Runs the Team Analytics tab in the Streamlit app."""
    matches_df, _ = process_match_data()
    selected_team, selected_team_2, selected_gender, selected_year = create_filters(
        matches_df
    )

    if selected_team == "All Teams":
        st.subheader("🗺️ World Cup Team Win Percentages")
        display_chart(world_cup_win_percentage_map(matches_df))

        st.subheader("📊 Top Goal-Scoring Teams")
        display_chart(plot_all_teams_summary(matches_df))

        show_fun_facts()
        display_trivia_section()

    else:
        # Validate data before proceeding
        filtered_df = validate_data(
            matches_df, selected_team, selected_team_2, selected_gender, selected_year
        )
        if filtered_df is None:
            return

        st.subheader("📈 Goal Distribution Over the Years")
        display_chart(
            goal_distribution_by_year_type_side_by_side(
                matches_df,
                selected_team,
                selected_team_2,
                selected_year,
                selected_gender,
            )
        )

        st.subheader(f"🏆 {selected_gender} Team Performance Breakdown")
        team_performance_pie(
            selected_team, selected_team_2, matches_df, selected_gender, selected_year
        )

        st.subheader(f"⚽ {selected_team} Match Score Distribution")
        display_chart(
            plot_wc_comparison(
                matches_df, selected_team, selected_gender, selected_team_2
            )
        )


# if __name__ == "__main__":
#   run_team_analytics_tab()
