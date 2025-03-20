# Project Milestones

## Milestone 1: Data Preprocessing & Generation
**Objective**  
Ensure that all relevant historical World Cup data (Fjelstul World Cup Database), NOAA weather data, and FIFA rankings are cleaned and consolidated.

**Key Tasks**  
- Gather and verify CSV files from the Fjelstul World Cup Database.  
- Identify and resolve missing or malformed entries.  
- Merge data into a unified structure (consistent column names, types, etc.).  
- Compute basic metrics (e.g., goals, match outcomes, average rankings).

**Success Criteria**  
- Data is free of duplicates and inconsistencies.  
- Core metrics (e.g., match results) are verified against known facts.  
- A single “master dataset” is produced, ready for advanced analytics and modeling.


## Milestone 2: Player & Team Analytics Development
**Objective**  
Deliver insightful **interactive dashboards** and analytics for both players and teams.

**Key Tasks**  
- Implement analytics specific data generation for advanced stats such as player imppacts.
- Create visual dashboards with charts that users can filter by player, team, or other parameters.  
- Integrate user controls (filters) to refine analytics views.

**Success Criteria**  
- Key metrics (e.g., scoring averages, penalty conversions, top scorers, clutch players etc) match expected values.  
- Visualization dashboards load without errors and respond to user input.  
- Users can easily interpret trends and make data-driven comparisons.


## Milestone 3: Feature Engineering & Model Training
**Objective**  
Build and validate a **machine learning model** that predicts match outcomes.

**Key Tasks**  
- Identify relevant features (e.g., ranking differentials, weather conditions).  
- Apply data transformations (e.g., one-hot encoding, scaling).  
- Train an ML model (e.g., classification) and tune hyperparameters if needed.  
- Evaluate performance (accuracy, F1 score) with test sets.

**Success Criteria**  
- Achieve a predetermined performance threshold.  
- Model is not overfitting. 
- A final, reproducible model is saved.

---

## Milestone 4: Web Application Integration
**Objective**  
Create and refine a **Streamlit**-based UI that unifies analytics and predictions.

**Key Tasks**  
- Set up a Streamlit app structure with tabs or sections (Analytics, Predictions).  
- Embed dashboards for player/team analytics.  
- Implement prediction forms where users can input match parameters (teams, temperature).  
- Retrieve and display the model’s predicted outcome (win, lose, or draw) plus a confidence score.

**Success Criteria**  
- The app runs end-to-end, from data loading to analytics display to model inference.  
- Users can navigate between analytics views and a prediction page without confusion.  
- The model responds to live inputs with accurate predictions.

---

## Milestone 5: Testing & Final Integration
**Objective**  
Validate each component and deliver a **production-ready** or **demo-ready** application.

**Key Tasks**  
- Write and run unit tests for each module (Data Manager, Analytics, Model, etc.).  
- Perform end-to-end tests: load data, generate metrics, visualize stats, and perform predictions.  
- Resolve integration issues between UI, data pipelines, and the ML model. 

**Success Criteria**  
- All tests pass consistently with acceptable coverage.  
- The application can predict as expected and handle unexpected inputs gracefully.  
- The application is stable enough to be demonstrated or deployed to end-users.