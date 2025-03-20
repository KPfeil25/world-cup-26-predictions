# Functional Specifications

The world cup is coming to North America and this **World Cup 2026 Prediction** app aims to empower different types of users—ranging from casual fans to coaches and sports bettors—to analyze historical World Cup data, generate visual analytics, and run predictive models for upcoming or hypothetical matches. Below, you’ll find background information, user profiles, data sources, core use cases, and user stories.


## 1. Background

The app allows users to:
- Explore historical World Cup data (e.g., match outcomes, player statistics, team performances).
- Run **predictive analyses** to forecast match outcomes based on factors like team form, weather conditions, and rankings.
- Visualize trends over time (e.g., how teams or players have performed in past tournaments).

By integrating data from multiple sources (Fjelstul World Cup Database, NOAA weather data, FIFA Rankings from Kaggle), the tool produces interactive dashboards and predictive models for various real-world scenarios. This app can be used by a wide range of users, such as a coach prepping for upcoming matches, a fan curious about their team’s chances, or a sports bettor weighing their odds.

## 2. User Profiles

1. **Fan (e.g., Dante Rossi)**
   - **Domain Knowledge**: Understands basic football/soccer concepts, team histories, star players.  
   - **Goal**: View team analytics, historical performance, and predictions for upcoming fixtures.  
   - **Technical Experience**: Non-technical; expects a plug-and-play UI.

2. **Sports Bettor (e.g., @San_Marina_SupaFan1)**
   - **Domain Knowledge**: Keen interest in odds, team form, and historical match outcomes.  
   - **Goal**: Access predictive analytics to inform betting decisions, evaluate past performance.  
   - **Technical Experience**: Moderately technical; comfortable reading analytics, might want an API to integrate with betting platforms.

3. **News Reporter (e.g., Charles Barkley)**
   - **Domain Knowledge**: Covers sports stories, seeks unique angles on team/ player performance.  
   - **Goal**: Quickly gather historical trends, create storylines based on historical and predicted data.  
   - **Technical Experience**: Non-technical; relies on a straightforward UI and visualizations.

4. **Coach (e.g., Pochettino)**
   - **Domain Knowledge**: Deep knowledge of soccer tactics and player abilities.  
   - **Goal**: Analyze upcoming opponents, explore individual player analytics, refine strategies.  
   - **Technical Experience**: Likely non-technical in programming terms but data-savvy.

5. **Technician / Model Maintainer (e.g., Micah Richards)**
   - **Domain Knowledge**: Skilled in Python, ML, data pipelines, FIFA Rankings.  
   - **Goal**: Regularly update or retrain predictive models as new data arrives, maintain the codebase.  
   - **Technical Experience**: Highly technical; needs direct access to APIs, code, and possibly containerized deployments or infrastructure.


## 3. Data Sources

1. [**Fjelstul World Cup Database**](https://github.com/jfjelstul/worldcup)  
   - Comprehensive dataset of World Cup matches, team stats, player stats, and stadiums.  
   - Source for historical performance and outcome data.

2. [**NOAA Weather Data**](https://www.ncei.noaa.gov/cdo-web/)  
   - Provides weather information, such as temperature, for the dates and locations of World Cup matches.  
   - Incorporated into the predictive model to see how weather might impact match outcomes.

3. **FIFA [Men Rankings](https://www.kaggle.com/datasets/cashncarry/fifaworldranking/data) and [Women Rankings](https://www.kaggle.com/datasets/cashncarry/fifa-world-ranking-women) Datasets (Kaggle)**  
   - Includes historical ranking data for men’s (1992 onward) and women’s (2003 onward) national teams.  
   - Allows the model to factor in relative team strength over time.

## 4. Use Cases

### Use Case 1: Filtering to a Specific Team to Generate Analytics
**Objective**: Choose a specific team to view performance trends.  
**Flow**:
1. **User** opens Analytics Page.  
2. **System** displays a list of teams.  
3. **User** selects a team.  
4. **System** fetches years in which the team participated.  
5. **User** chooses a specific year.  
6. **System** generates and displays relevant graphs/analytics.

### Use Case 2: Predicting Matches
**Objective**: Forecast the outcome of a hypothetical match between two teams.  
**Flow**:
1. **User** opens the Predictions Page.  
2. **System** presents two dropdowns for team selection.  
3. **User** selects both teams.  
4. **System** prompts for weather conditions.  
5. **User** inputs weather data (e.g., temperature).  
6. **System** validates the input; if valid, generates a predicted outcome and displays confidence. Otherwise, prompts user to correct input.

### Use Case 3: Comparing Two Players
**Objective**: Compare two players based on a few specific statistics.  
**Flow**:
1. **User** opens the Player Analytics page.  
2. **System** shows a list of players or a search box.  
3. **User** selects or searches for two players to compare.  
4. **System** presents that player’s statistics (matches played, goals, appearances, etc.).    
5. **System** displays a relevant comparison table and graph.

### Use Case 4: Adding a Non-Participant Team to a Past World Cup
**Objective**: Explore a “what-if” scenario for a team that did not qualify.  
**Flow**:
1. **User** opens the Predictive Page.  
2. **System** shows teams who have missed out on at least one WC.  
3. **User** selects a team.  
4. **System** displays years that this team did not qualify.  
5. **User** selects a year.  
6. **System** outlines the original qualification path and offers an “alternate reality” button.  
7. **User** clicks the button.  
8. **System** simulates how the team might have performed, using the existing predictive model.

### Use Case 5: Viewing Results Over Time for a Specific Country
**Objective**: Generate a graph of historical finishes or achievements.  
**Flow**:
1. **User** clicks on the Analytics page.  
2. **System** displays the analytics homepage.  
3. **User** selects a country from a dropdown.  
4. **System** generates a timeline or progress chart showing the country’s finishes over multiple World Cups.


## 5. User Stories

### 5.1 Fan (Dante Rossi)
- **Wants**:  
  - To filter and explore a specific team’s historic and upcoming performance.  
  - Predict how their favorite team might perform in the next match.  
- **Constraints**:  
  - Non-technical, needs an easy-to-use interface.

### 5.2 Sports Bettor (@San_Marina_SupaFan1)
- **Wants**:  
  - In-depth predictive analytics to inform betting decisions.  
  - Past performance data for thorough analysis.  
- **Interaction**:  
  - Through a user-friendly UI or a possible API if advanced.  
- **Constraints**:  
  - Moderately technical, comfortable with data but not coding.

### 5.3 News Reporter (Charles Barkley)
- **Wants**:  
  - Historical trends and unique storylines for upcoming matches.  
  - Quick stats on teams, players, or unusual patterns.  
- **Constraints**:  
  - Non-technical, expects intuitive dashboards.

### 5.4 Coach (Pottechitino)
- **Wants**:  
  - Opponent analytics to refine match tactics.  
  - Individual player analytics for scouting and preparation.  
- **Constraints**:  
  - Data-savvy but not a programmer, relies on robust UI visualizations.

### 5.5 Technician / Model Maintainer (Micah Richards)
- **Wants**:  
  - Access to the codebase to update data ingestion, retrain or tune the ML model as new data arrives.  
  - An integrated environment (scripts, APIs) for quick iteration.  
- **Constraints**:  
  - Highly technical, needs well-organized code and accurate data pipelines.