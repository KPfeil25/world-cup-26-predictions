'''
NAME:
    predictions_app - Streamlit web application for World Cup 2026 match predictions

DESCRIPTION:
    This module implements a user-friendly web interface for predicting soccer match outcomes
    for the 2026 World Cup. It allows users to select teams, stadiums, and match conditions,
    then generates predictions based on the trained machine learning model. The app displays
    team information, player rosters, prediction results, and visualizations of
    outcome probabilities.

FUNCTIONS:
    run_prediction_app - Main function that runs the entire Streamlit application
    load_data - Loads all necessary data files and models
    get_stadiums_mapping - Creates a mapping between stadium IDs and names
    get_available_years - Retrieves years when a team participated in World Cup
    get_team_players - Gets player roster for a given team and year
    get_team_award_count - Retrieves the number of awards for a team
    predict_match - Prepares data and predicts match outcome

FILE:
    /tmp/world_cup_26_predictions/predictions/predictions_app.py
'''

from pathlib import Path
import joblib
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import _column_transformer

if not hasattr(_column_transformer, "_RemainderColsList"):
    class _RemainderColsList(list):
        """Backward-compatible placeholder for sklearn 1.6 pickles."""

    setattr(_column_transformer, "_RemainderColsList", _RemainderColsList)


def get_stadiums_mapping(matches_data):
    '''
    Creates a mapping between stadium IDs and stadium names.

    Args:
        matches_data (pandas.DataFrame): DataFrame containing match data with stadium information

    Returns:
        dict: Dictionary mapping stadium IDs to stadium names
    '''
    if 'stadium_id' in matches_data.columns and 'stadium_name' in matches_data.columns:
        return dict(zip(matches_data['stadium_id'], matches_data['stadium_name']))
    if 'stadium_id' in matches_data.columns:
        return {sid: f"Stadium {sid}" for sid in matches_data['stadium_id'].unique()}
    return {}


def get_available_years(team_name, gender, matches_data):
    '''
    Retrieves years when a team participated in World Cup tournaments.

    Filters match data to find years when the specified team participated
    in tournaments of the specified gender. Always includes 2026 as an option
    for future predictions.

    Args:
        team_name (str): Name of the team
        gender (str): "Men" or "Women"
        matches_data (pandas.DataFrame): DataFrame containing match data

    Returns:
        list: Sorted list of years when the team participated in World Cup tournaments
    '''
    gender_filter = 'Men' if gender == "Men" else 'Women'
    team_matches = matches_data[
        (matches_data['tournament_name'].str.contains(gender_filter)) &
        ((matches_data['home_team_name'] == team_name) |
         (matches_data['away_team_name'] == team_name))]

    if 'year' not in team_matches.columns and 'match_date' in team_matches.columns:
        team_matches['year'] = pd.to_datetime(team_matches['match_date']).dt.year
    years = sorted(team_matches['year'].unique(), reverse=True)
    if 2026 not in years:
        years = [2026] + years
    return years


def get_team_award_count(team_name, awards_data):
    '''
    Retrieves the number of awards for a team.

    Counts the number of awards won by the specified team using case-insensitive matching.

    Args:
        team_name (str): Name of the team
        awards_data (pandas.DataFrame): DataFrame containing award information

    Returns:
        int: Number of awards won by the team
    '''
    if awards_data is None or awards_data.empty:
        return 0
    team_data = awards_data[awards_data['team_name'].str.lower() == team_name.lower()]
    return len(team_data)


def fix_name(raw_name):
    """
    Cleans up a raw name value by trimming and handling
    not-applicable values.
    
    Args:
        raw_name: The raw name value which might be null or contain "N/A" variants
        
    Returns:
        str: Cleaned name string or empty string if not applicable
    """
    if pd.isnull(raw_name):
        return ""
    val = str(raw_name).strip().lower()
    if val in ("not applicable", "n/a", "na", "not available"):
        return ""
    return str(raw_name).strip()

def get_team_players(team_name, gender, year, players_data):
    '''
    Gets player roster for a given team and year.

    For historical years, retrieves the actual player list. For 2026 predictions,
    uses the most recent available data for the team. Handles various data formats
    and missing information gracefully.

    Args:
        team_name (str): Name of the team
        gender (str): "Men" or "Women"
        year (int): Year to retrieve players for (or 2026 for prediction)
        players_data (pandas.DataFrame): DataFrame containing player appearance data

    Returns:
        list: List of player names for the specified team and year
    '''
    if 'team_name' not in players_data.columns:
        return ["No team_name column in player data"]
    gender_filter = 'Men' if gender == "Men" else 'Women'
    gender_players = players_data[players_data['tournament_name'].str.contains(
        gender_filter, na=False)]
    if 'player_name' not in gender_players.columns and 'given_name' in gender_players.columns:
        if 'family_name' in gender_players.columns:
            gender_players['given_name'] = gender_players['given_name'].apply(fix_name)
            gender_players['family_name'] = gender_players['family_name'].apply(fix_name)
            gender_players['player_name'] = (gender_players['given_name'].fillna('') + ' ' +
                                      gender_players['family_name'].fillna(''))
            gender_players['player_name'] = gender_players['player_name'].str.strip()
            gender_players.loc[
                gender_players['player_name'] == '', 'player_name'] = "Unknown Player"
    if 'player_name' not in gender_players.columns:
        return ["No player name columns available in data"]
    return _get_players_by_year(gender_players, team_name, year)


def _get_players_by_year(players_df, team_name, year):
    """
    Helper function to get players from a specific year or most recent year for 2026.
    
    Args:
        players_df (pandas.DataFrame): DataFrame with filtered player data
        team_name (str): Team name to filter by
        year (int): Year to filter by, or 2026 for most recent data
        
    Returns:
        list: List of player names
    """
    if year == 2026:
        team_data = players_df[players_df['team_name'] == team_name]
        if team_data.empty:
            return ["No player data available for this team"]

        recent_years = team_data['year'].unique()
        if not recent_years.size:
            return ["No player data available for this team"]

        most_recent_year = max(recent_years)
        team_players = team_data[team_data['year'] == most_recent_year]
    else:
        team_players = players_df[(players_df['team_name'] == team_name) &
                                  (players_df['year'] == year)]

    if team_players.empty:
        return ["No players found for this team/year"]

    team_players = team_players.drop_duplicates('player_name')

    if 'position_code' in team_players.columns:
        position_order = {'GK': 1, 'DF': 2, 'MF': 3, 'FW': 4}
        team_players['pos_order'] = team_players['position_code'].map(
            lambda x: position_order.get(x, 5))
        team_players = team_players.sort_values('pos_order')

    return team_players['player_name'].tolist()


def get_team_rank(team_name, rankings_df, default_rank=50):
    """
    Get team rank from rankings DataFrame.
    
    Args:
        team_name (str): Team name
        rankings_df (pandas.DataFrame): DataFrame with rankings data
        default_rank (int): Default rank to use if team not found
        
    Returns:
        int: Team rank
    """
    if team_name in rankings_df['team'].values:
        return rankings_df[rankings_df['team'] == team_name]['rank'].values[0]
    return default_rank


def get_city_name(stadium_id, matches_df, default_name='Unknown'):
    """
    Get city name for a stadium ID.
    
    Args:
        stadium_id (int): Stadium ID
        matches_df (pandas.DataFrame): DataFrame with match data
        default_name (str): Default name to use if not found
        
    Returns:
        str: City name
    """
    stadium_matches = matches_df[matches_df['stadium_id'] == stadium_id]
    if not stadium_matches.empty:
        return stadium_matches['city_name'].iloc[0]
    return default_name


def get_player_info(home_team, away_team, players_df):
    """
    Get player IDs and position code for match prediction.
    
    Args:
        home_team (str): Home team name
        away_team (str): Away team name
        players_df (pandas.DataFrame): DataFrame with player data
        
    Returns:
        tuple: (home_player_id, away_player_id, position_code)
    """
    home_player_id = np.nan
    away_player_id = np.nan
    home_players = players_df[players_df['team_name'] == home_team]
    away_players = players_df[players_df['team_name'] == away_team]
    if not home_players.empty:
        home_player_id = home_players['player_id'].iloc[0]
    if not away_players.empty:
        away_player_id = away_players['player_id'].iloc[0]
    position_code = 'GK'
    if not players_df.empty and 'position_code' in players_df.columns:
        position_counts = players_df['position_code'].value_counts()
        if not position_counts.empty:
            position_code = position_counts.index[0]
    return home_player_id, away_player_id, position_code


def extract_team_data(team_name, gender, data_dict):
    """
    Extract team-specific data for match prediction.
    
    Args:
        team_name (str): Team name
        gender (str): 'Men' or 'Women'
        data_dict (dict): Dictionary with loaded data
        
    Returns:
        tuple: (team_rank, award_count)
    """
    rankings = data_dict['mens_rankings'] if gender == 'Men' else data_dict['womens_rankings']
    team_rank = get_team_rank(team_name, rankings)
    award_count = get_team_award_count(team_name, data_dict['awards'])
    return team_rank, award_count

def create_match_data(match_info, data_dict):
    """
    Create match data DataFrame for prediction.
    
    Args:
        match_info (dict): Dictionary with match details
        data_dict (dict): Dictionary with loaded data
        
    Returns:
        pandas.DataFrame: DataFrame with match data ready for prediction
    """
    home_team = match_info['home_team']
    away_team = match_info['away_team']
    stadium_id = match_info['stadium_id']
    temperature = match_info['temperature']
    gender = match_info['gender']
    home_rank, home_award_count = extract_team_data(home_team, gender, data_dict)
    away_rank, away_award_count = extract_team_data(away_team, gender, data_dict)
    city_name = get_city_name(stadium_id, data_dict['matches'])
    home_player_id, away_player_id, position_code = get_player_info(
        home_team, away_team, data_dict['players'])
    return pd.DataFrame({
        'stage_name': ['Group stage'],
        'stadium_id': [stadium_id],
        'city_name': [city_name],
        'home_team_name': [home_team],
        'away_team_name': [away_team],
        'extra_time': [False],
        'penalty_shootout': [False],
        'home_player_id': [home_player_id],
        'position_code': [position_code],
        'away_player_id': [away_player_id],
        'home_team_award_count': [home_award_count],
        'away_team_award_count': [away_award_count],
        'avg_temp': [temperature],
        'year': [2026],
        'home_team_rank': [home_rank],
        'away_team_rank': [away_rank]
    })


def calculate_confidence(model, match_data, default_confidence=70):
    """
    Calculate confidence score for prediction.
    
    Args:
        model: Trained prediction model 
        match_data (pandas.DataFrame): Data for prediction
        default_confidence (int): Default confidence value
        
    Returns:
        float: Confidence percentage
    """
    try:
        probabilities = model.predict_proba(match_data)[0]
        return max(probabilities) * 100
    except AttributeError:
        return default_confidence


def predict_match(match_info, data_dict):
    '''
    Prepares data and predicts match outcome.

    Assembles all necessary data for prediction, including team rankings, award counts,
    stadium information, and player data. Uses the trained model to predict the match result
    and calculates confidence scores.

    Args:
        match_info (dict): Dictionary containing match details:
            - home_team: Name of the home team
            - away_team: Name of the away team
            - stadium_id: ID of the stadium
            - temperature: Match temperature in Celsius
            - gender: "Men" or "Women"
        data_dict (dict): Dictionary containing all loaded data

    Returns:
        tuple: A tuple containing:
            - result (str): Predicted match result ("win", "loss", or "draw")
            - confidence (float): Confidence percentage for the prediction
    '''
    model = data_dict['model']
    le = data_dict['le']
    new_match_data = create_match_data(match_info, data_dict)
    prediction_encoded = model.predict(new_match_data)
    result = le.inverse_transform(prediction_encoded)[0]
    confidence = calculate_confidence(model, new_match_data)
    return result, confidence


@st.cache_data
def load_data():
    '''
    Loads all necessary data files and models for match predictions.

    Uses Streamlit's caching mechanism to efficiently load data files including
    matches, rankings, temperatures, awards, and player information. Also loads
    the trained prediction model and label encoder.

    Returns:
        dict: Dictionary containing all loaded data:
            - matches: Historical match data
            - mens_rankings: FIFA men's team rankings
            - womens_rankings: FIFA women's team rankings
            - temperature: Temperature data for match locations
            - awards: Award winner information
            - players: Player appearance data
            - model: Trained prediction model
            - le: Label encoder for prediction outputs
    '''
    data_dict = {}
    try:
        base_path = Path(__file__).resolve().parents[1]
        data_dir = base_path / "data"
        model_dir = base_path / "predictions"

        data_dict['matches'] = pd.read_csv(data_dir / "matches.csv")
        data_dict['mens_rankings'] = pd.read_csv(data_dir / "fifa_mens_rankings.csv")
        data_dict['womens_rankings'] = pd.read_csv(data_dir / "fifa_womens_rankings.csv")
        data_dict['temperature'] = pd.read_csv(data_dir / "temperatures_partitioned.csv")
        data_dict['awards'] = pd.read_csv(data_dir / "award_winners.csv")
        data_dict['players'] = pd.read_csv(data_dir / "player_appearances.csv")
        if 'year' not in data_dict['players'].columns and 'match_date' in data_dict[
            'players'].columns:
            data_dict['players']['year'] = pd.to_datetime(data_dict['players'][
                'match_date']).dt.year
        data_dict['model'] = joblib.load(model_dir / "model.pkl")
        data_dict['le'] = joblib.load(model_dir / "label_encoder.pkl")
        return data_dict
    except FileNotFoundError as file_error:
        st.error(f"Required data file not found: {file_error}")
        return None

def get_country_code(team_name):
    """
    Convert team name to 2-letter ISO country code.
    
    Args:
        team_name (str): Name of the country/team
        
    Returns:
        str: 2-letter ISO country code or None if not found
    """
    country_map = {
        "Algeria": "dz",
        "Angola": "ao",
        "Argentina": "ar",
        "Australia": "au",
        "Austria": "at",
        "Belgium": "be",
        "Bolivia": "bo",
        "Bosnia and Herzegovina": "ba",
        "Brazil": "br",
        "Bulgaria": "bg",
        "Cameroon": "cm",
        "Canada": "ca",
        "Chile": "cl",
        "China": "cn",
        "Chinese Taipei": "tw",
        "Colombia": "co",
        "Costa Rica": "cr",
        "Croatia": "hr",
        "Cuba": "cu",
        "Czech Republic": "cz",
        "Czechoslovakia": "cz",
        "Denmark": "dk",
        "Dutch East Indies": "id",
        "East Germany": "de",
        "Ecuador": "ec",
        "Egypt": "eg",
        "El Salvador": "sv",
        "England": "gb-eng",
        "Equatorial Guinea": "gq",
        "France": "fr",
        "Germany": "de",
        "Ghana": "gh",
        "Greece": "gr",
        "Haiti": "ht",
        "Honduras": "hn",
        "Hungary": "hu",
        "Iceland": "is",
        "Iran": "ir",
        "Iraq": "iq",
        "Israel": "il",
        "Italy": "it",
        "Ivory Coast": "ci",
        "Jamaica": "jm",
        "Japan": "jp",
        "Kuwait": "kw",
        "Mexico": "mx",
        "Morocco": "ma",
        "Netherlands": "nl",
        "New Zealand": "nz",
        "Nigeria": "ng",
        "North Korea": "kp",
        "Northern Ireland": "gb-nir",
        "Norway": "no",
        "Panama": "pa",
        "Paraguay": "py",
        "Peru": "pe",
        "Poland": "pl",
        "Portugal": "pt",
        "Qatar": "qa",
        "Republic of Ireland": "ie",
        "Romania": "ro",
        "Russia": "ru",
        "Saudi Arabia": "sa",
        "Scotland": "gb-sct",
        "Senegal": "sn",
        "Serbia": "rs",
        "Serbia and Montenegro": "rs",
        "Slovakia": "sk",
        "Slovenia": "si",
        "South Africa": "za",
        "South Korea": "kr",
        "Soviet Union": "ru",
        "Spain": "es",
        "Sweden": "se",
        "Switzerland": "ch",
        "Thailand": "th",
        "Togo": "tg",
        "Trinidad and Tobago": "tt",
        "Tunisia": "tn",
        "Turkey": "tr",
        "Ukraine": "ua",
        "United Arab Emirates": "ae",
        "United States": "us",
        "Uruguay": "uy",
        "Wales": "gb-wls",
        "West Germany": "de",
        "Yugoslavia": "rs",
        "Zaire": "cd"
    }
    return country_map.get(team_name)

def display_team_info(team_data, column, data_dict):
    """
    Display team information in the specified column.
    
    Args:
        team_data (dict): Dictionary with team name and year
        column: Streamlit column to display information in
        data_dict (dict): Data dictionary
    """
    team_name = team_data['name']
    team_year = team_data['year']
    gender = team_data['gender']
    country_code = get_country_code(team_name)
    with column:
        st.subheader(f"{team_name}")
        st.markdown(f"### {team_name} ({team_year})")
        if country_code:
            st.image(f"https://flagcdn.com/w160/{country_code.lower()}.png", width=150)
        else:
            st.image(f"https://via.placeholder.com/150?text={team_name}", width=150)
        team_awards = get_team_award_count(team_name, data_dict['awards'])
        st.markdown(f"**Awards:** {team_awards}")
        st.markdown("#### Players:")
        team_players = get_team_players(team_name, gender, team_year, data_dict['players'])
        for player in team_players:
            st.write(player)


def display_outcome(home_team, away_team, result):
    """
    Display the match outcome prediction.
    
    Args:
        home_team (str): Home team name
        away_team (str): Away team name  
        result (str): Match result
    """
    win_outcomes = {'win', 'home team win'}
    loss_outcomes = {'loss', 'away team win'}
    if result in win_outcomes:
        st.success(f"**{home_team}** is predicted to win against {away_team}")
    elif result in loss_outcomes:
        st.error(f"**{away_team}** is predicted to win against {home_team}")
    else:
        st.info(
            f"The match between **{home_team}** and **{away_team}** is predicted to end in a draw")


def prepare_visualization_data(match_result):
    """
    Prepare data for visualization chart.
    
    Args:
        match_result (dict): Dictionary with match result data
        
    Returns:
        pandas.DataFrame: Melted DataFrame for charting
    """
    home_team = match_result['home_team']
    away_team = match_result['away_team']
    home_year = match_result['home_year']
    away_year = match_result['away_year']
    result = match_result['result']
    confidence = match_result['confidence']
    win_outcomes = {'win', 'home team win'}
    loss_outcomes = {'loss', 'away team win'}
    if result in win_outcomes:
        home_prob = confidence
        away_prob = (100-confidence)*0.6
        draw_prob = (100-confidence)*0.4
    elif result in loss_outcomes:
        away_prob = confidence
        home_prob = (100-confidence)*0.6
        draw_prob = (100-confidence)*0.4
    else:
        draw_prob = confidence
        home_prob = (100-confidence)/2
        away_prob = (100-confidence)/2
    result_df = pd.DataFrame({
        'Team': [f"{home_team} ({home_year})", f"{away_team} ({away_year})"],
        'Win Probability': [home_prob, away_prob],
        'Draw Probability': [draw_prob, draw_prob]
    })
    return pd.melt(
        result_df,
        id_vars=['Team'],
        var_name='Outcome',
        value_name='Probability'
    )


def display_chart(result_df_melted):
    """
    Display altair chart with prediction probabilities.
    
    Args:
        result_df_melted (pandas.DataFrame): Melted DataFrame for charting
    """
    chart = alt.Chart(result_df_melted).mark_bar().encode(
        x=alt.X('Team:N', title=None),
        y=alt.Y('Probability:Q', title='Probability (%)'),
        color=alt.Color('Outcome:N', scale=alt.Scale(
            domain=['Win Probability', 'Draw Probability'],
            range=['#1f77b4', '#ff7f0e']
        )),
        tooltip=['Team', 'Outcome', 'Probability']
    ).properties(
        width=300,
        height=200,
        title='Match Outcome Probabilities'
    )
    st.altair_chart(chart)


def display_match_details(match_info, data_dict):
    """
    Display match details section.
    
    Args:
        match_info (dict): Match information
        data_dict (dict): Data dictionary
    """
    home_team = match_info['home_team']
    away_team = match_info['away_team']
    stadium_name = match_info['stadium_name']
    stadium_id = match_info['stadium_id']
    temperature = match_info['temperature']
    st.markdown("#### Match Details")
    st.markdown(f"**Stadium:** {stadium_name} (ID: {stadium_id})")
    st.markdown(f"**Temperature:** {temperature}°C")
    home_awards_count = get_team_award_count(home_team, data_dict['awards'])
    away_awards_count = get_team_award_count(away_team, data_dict['awards'])
    st.markdown(f"**Home Team Awards:** {home_awards_count}")
    st.markdown(f"**Away Team Awards:** {away_awards_count}")


def display_prediction_context():
    """Display prediction context information."""
    st.markdown("#### Prediction Context")
    st.markdown("""
        This prediction is based on historical team performance, player statistics, 
        and match conditions. The model considers:
        - Team rankings
        - Previous World Cup performances
        - Award history
        - Stadium factors
        - Weather conditions
    """)


def display_prediction_results(match_info, result_data, data_dict):
    """
    Display prediction results.
    
    Args:
        match_info (dict): Dictionary with match settings
        result_data (dict): Dictionary with prediction results
        data_dict (dict): Data dictionary
    """
    match_result = {
        'home_team': match_info['home_team'],
        'away_team': match_info['away_team'],
        'home_year': match_info['home_year'],
        'away_year': match_info['away_year'],
        'result': result_data['result'],
        'confidence': result_data['confidence']
    }
    st.markdown("### Prediction Result")
    display_outcome(match_result['home_team'], match_result['away_team'], match_result['result'])
    st.write(f"Confidence: {match_result['confidence']:.1f}%")
    result_df_melted = prepare_visualization_data(match_result)
    display_chart(result_df_melted)
    display_match_details(match_info, data_dict)
    display_prediction_context()


def prepare_stadium_options(matches_data, stadium_map):
    """
    Prepare stadium selection options and display text.
    
    Args:
        matches_data (pandas.DataFrame): Match data
        stadium_map (dict): Stadium ID to name mapping
        
    Returns:
        tuple: (stadium_options list, stadium_display list)
    """
    stadium_options = []
    stadium_display = []
    for stadium_id in sorted(matches_data['stadium_id'].unique()):
        stadium_options.append(stadium_id)
        stadium_name = stadium_map.get(stadium_id, f"Stadium {stadium_id}")
        stadium_display.append(f"{stadium_name} (ID: {stadium_id})")
    return stadium_options, stadium_display



def get_filtered_teams(matches_data, gender):
    """
    Get teams filtered by gender.
    
    Args:
        matches_data (pandas.DataFrame): Match data
        gender (str): 'Men' or 'Women'
        
    Returns:
        list: Sorted list of team names
    """
    gender_filter = 'Men' if gender == "Men" else 'Women'
    mask = matches_data['tournament_name'].str.contains(gender_filter)
    return sorted(matches_data[mask]['home_team_name'].unique())

def select_teams_and_years(teams, gender, matches_data, column):
    """
    Handle team and year selection UI.
    
    Args:
        teams (list): List of team names
        gender (str): 'Men' or 'Women'
        matches_data (pandas.DataFrame): Match data
        column: Streamlit column to use
        
    Returns:
        tuple: (home_team, away_team, home_year, away_year)
    """
    with column:
        home_team = st.selectbox("Select Home Team", teams, key="home_team")
        away_team_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Select Away Team", away_team_options, key="away_team")
        home_years = get_available_years(home_team, gender, matches_data)
        away_years = get_available_years(away_team, gender, matches_data)
        col_home_year, col_away_year = st.columns(2)
        with col_home_year:
            home_year = st.selectbox(f"{home_team} Year", home_years, key="home_year")
        with col_away_year:
            away_year = st.selectbox(f"{away_team} Year", away_years, key="away_year")
    return home_team, away_team, home_year, away_year

def select_stadium_and_temperature(stadium_options, stadium_display, column):
    """
    Handle stadium and temperature selection UI.
    
    Args:
        stadium_options (list): List of stadium IDs
        stadium_display (list): List of stadium display names
        column: Streamlit column to use
        
    Returns:
        tuple: (stadium_id, stadium_name, temperature)
    """
    with column:
        stadium_index = st.selectbox(
            "Select Stadium", 
            range(len(stadium_options)),
            format_func=lambda x: stadium_display[x]
        )
        selected_stadium_id = stadium_options[stadium_index]
        selected_stadium_name = stadium_display[stadium_index].split(" (ID:")[0]
        temperature = st.slider("Temperature (°C)", 5, 45, 25)
    return selected_stadium_id, selected_stadium_name, temperature

def configure_match_settings(data_dict, stadium_map, column):
    """
    Configure match settings UI in the provided column.
    
    Args:
        data_dict (dict): Data dictionary
        stadium_map (dict): Stadium ID to name mapping
        column: Streamlit column to use
        
    Returns:
        dict: Dictionary with all match settings
    """
    with column:
        st.subheader("Match Settings")
        gender = st.selectbox("Select Competition", ["Men", "Women"])
        teams = get_filtered_teams(data_dict['matches'], gender)
        home_team, away_team, home_year, away_year = select_teams_and_years(
            teams, gender, data_dict['matches'], column)
        stadium_options, stadium_display = prepare_stadium_options(
            data_dict['matches'], stadium_map)
        stadium_id, stadium_name, temperature = select_stadium_and_temperature(
            stadium_options, stadium_display, column)
        st.markdown(f"**Competition:** {gender}'s World Cup 2026")
        return {
            'gender': gender,
            'home_team': home_team,
            'away_team': away_team,
            'home_year': home_year,
            'away_year': away_year,
            'stadium_id': stadium_id,
            'stadium_name': stadium_name,
            'temperature': temperature
        }

def handle_prediction(match_settings, data_dict, column):
    """
    Handle prediction in the specified column.
    
    Args:
        match_settings (dict): Match settings
        data_dict (dict): Data dictionary
        column: Streamlit column to use
    """
    with column:
        if st.button("Predict Match Result"):
            match_info = {
                'home_team': match_settings['home_team'],
                'away_team': match_settings['away_team'],
                'stadium_id': match_settings['stadium_id'],
                'temperature': match_settings['temperature'],
                'gender': match_settings['gender']
            }
            result, confidence = predict_match(match_info, data_dict)
            result_data = {
                'result': result,
                'confidence': confidence
            }
            display_prediction_results(match_settings, result_data, data_dict)

def run_prediction_app():
    '''
    Main function that runs the entire Streamlit application.
    
    Sets up the user interface layout, manages user interactions, and coordinates
    the data loading, predictions, and visualization functionality. Organizes the
    application into three columns for home team, match settings, and away team.
    '''
    st.markdown("""
        This tool predicts the outcome of a match between two teams in the 2026 World Cup.
        Select gender, teams (including historical year for each team), stadium, and temperature to get a prediction.
    """)
    data_dict = load_data()

    if not data_dict:
        st.error("Failed to load data. Please check that all required files are available.")
        return
    stadium_map = get_stadiums_mapping(data_dict['matches'])
    col1, col2, col3 = st.columns([2, 3, 2])
    match_settings = configure_match_settings(data_dict, stadium_map, col2)
    home_team_data = {
        'name': match_settings['home_team'],
        'year': match_settings['home_year'],
        'gender': match_settings['gender']
    }
    away_team_data = {
        'name': match_settings['away_team'],
        'year': match_settings['away_year'],
        'gender': match_settings['gender']
    }
    display_team_info(home_team_data, col1, data_dict)
    display_team_info(away_team_data, col3, data_dict)
    handle_prediction(match_settings, data_dict, col2)
    st.markdown("---")
    st.markdown("World Cup 2026 Prediction Tool")

if __name__ == "__main__":
    run_prediction_app()
