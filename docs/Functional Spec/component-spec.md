# Component Specification

## 1. Data
Raw information powering the World Cup 2026 Prediction Application.

**Description**  
- Collects **historical World Cup data** from the Fjelstul World Cup Database, which provides comprehensive details about every World Cup (players, teams, statistics, stadiums, etc).  
- Incorporates **weather data** from NOAA to identify average temperatures for match locations—this weather metric is used as part of the prediction model.  
- Includes **FIFA Rankings data** from Kaggle, going back to 1992 for men’s teams and 2003 for women’s teams. The model uses an average ranking derived from these values.

**Inputs**  
- *Data sources*, such as CSV files from the Fjelstul World Cup Database, NOAA datasets, and the Kaggle FIFA Rankings dataset.

**Outputs**  
- Data stored in the project repository, ready for ingestion by the Data Manager.

**Assumptions**  
- All source data is accurate, correctly formatted, and well-structured.  
- Sufficient data exists to support meaningful analysis and predictions.


## 2. Data Manager
Responsible for **gathering, ingesting, cleaning, and transforming** raw data.

**Description**  
- Reads raw data from the project repository.  
- Cleans and merges datasets (handling missing values, outliers, etc.) to produce a unified data table.  
- Outputs a consistent dataset ready for further transformations.

**Inputs**  
- *Data sources* (e.g., CSV files containing historical matches, weather data, player/team stats).

**Outputs**  
- **Processed data** in a standardized DataFrame (clean columns, unified formats).

**Assumptions**  
- Data is saved in the project repository and can be loaded into in-memory data structures.  
- Data follows consistent formatting rules, allowing cleaning and merging to work effectively.


## 3. Data Generation & Pre-Processing
Generates **summaries, aggregates, or analysis-specific metrics** for analytics.

**Description**  
- Uses the cleaned dataset from the Data Manager to compute additional metrics such as total goals scored, wins, losses, penalties converted, or other domain-specific statistics.

**Inputs**  
- **Processed data** from the Data Manager.

**Outputs**  
- **Enhanced data** that includes new columns for summary and aggregated metrics (e.g., average goals, total player appearances, penalty conversions).

**Assumptions**  
- The processed data has all required columns and a consistent structure for calculating summary statistics.


## 4. Feature Engineering
Transforms and creates new variables for **model training**.

**Description**  
- Selects and encodes the most relevant features (e.g., via categorical encoding or scaling).  
- Produces a **feature set** suitable for feeding into a machine learning algorithm.

**Inputs**  
- **Processed or enhanced data** (depending on your pipeline design).

**Outputs**  
- **Model features** (a DataFrame or array) optimized for training (one-hot encoded, normalized/standardized, etc.).

**Assumptions**  
- Feature transformations remain consistent between training and inference.  
- There are enough meaningful variables to produce an effective predictive model.


## 5. ML Training Component
Trains and stores the **predictive model**.

**Description**  
- Consumes the engineered features to train a suitable machine learning model.  
- Evaluates performance using metrics like accuracy or F1 score and may fine-tune hyperparameters.  
- Stores the trained model weights for subsequent use in prediction.

**Inputs**  
- **Model features** from the Feature Engineering step.  
- **Labels or target values** (e.g., actual match outcomes).

**Outputs**  
- **Trained model weights** (saved to file or memory).  
- **Evaluation metrics** (e.g., accuracy, F1 score).

**Assumptions**  
- The training dataset is representative of the target scenarios.  
- The pipeline includes appropriate validation or cross-validation to prevent overfitting.


## 6. Model Prediction
Uses the **stored model** to forecast outcomes based on user or new data inputs.

**Description**  
- Loads the pre-trained model and applies it to incoming feature sets (team matchups, weather conditions, etc.).  
- Returns a predicted match result (win, lose) along with a confidence score.

**Inputs**  
- **User-defined parameters** (e.g., team names, stadium, temperature).  
- **Trained model** (loaded from file or persisted in memory).

**Outputs**  
- **Predicted outcome** (win, lose, or draw).  
- **Confidence score** for the predicted result.

**Assumptions**  
- The same feature engineering processes are applied to new data as were applied during training.  
- Model weights are accessible and compatible with the prediction environment.


## 7. Analytics Component
Generates **interactive graphs, tables, or dashboards** for exploring data insights.

**Description**  
- Uses **enhanced data** (including summaries and aggregates) to create analytics-focused visualizations (e.g., leaderboard charts, distribution plots, etc.).

**Inputs**  
- **Enhanced data** from Data Generation & Pre-Processing.  
- **Query parameters** (team, player, time range, gender, country, etc.).

**Outputs**  
- **Visualizations** (charts, tables, or dashboards) that can be embedded into the web UI.

**Assumptions**  
- Users provide valid queries that align with the available dataset.  
- Visualization libraries (e.g., Plotly, Matplotlib) are installed and properly configured.


## 8. Web UI / Dashboard
Brings all components together into a **user-friendly web interface**.

**Description**  
- A front-end application (based on **Streamlit**) offering multiple tabs or sections:
  - **Analytics**: Explore historical data, aggregated statistics, and visual insights for players and teams.  
  - **Prediction**: Input match parameters (teams, stadium, weather) and view predicted outcomes.
- Orchestrates calls to each component: from data ingestion and analytics to predictions.

**Inputs**  
- **Visualizations** generated by the Analytics Component.  
- **User inputs** (e.g., desired match scenario) for the Prediction Component.

**Outputs**  
- **Rendered UI** with navigable tabs for analytics and predictions.  
- **User-facing model results** (predicted outcome, confidence score).

**Assumptions**  
- All backend components (data pipelines, models) are in working condition and produce valid outputs.  
- The Streamlit environment can handle the dataset size and provide interactive elements effectively.

## Overall Component Architecture - Overall Flow Chart
![World Cup Prediction - Overall Flow Chart](../Diagrams/World%20Cup%20Prediction%20-%20Overall%20Flow%20Chart.png)