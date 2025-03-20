# world-cup-26-predictions
## Build Status and Test Coverage
[![build_test](https://github.com/KPfeil25/world-cup-26-predictions/actions/workflows/build_test.yml/badge.svg?branch=main)](https://github.com/KPfeil25/world-cup-26-predictions/actions/workflows/build_test.yml)
[![Coverage Status](https://coveralls.io/repos/github/KPfeil25/world-cup-26-predictions/badge.svg)](https://coveralls.io/github/KPfeil25/world-cup-26-predictions)

## Project Type:
The project will be **analytical** in nature and we will also be **creating a tool** to demonstrate the predictive element of our project.

## Team Members
Jacob Miller \
Richard Pallangyo \
Akshat Pandey \
Kevin Pfeil

## Project Goals:
- Provide weather conditions, teams, stadiums, match statistics, etc. 
- Provide insights into past matches with similar conditions
- Provide predictions on who will win using a ML model
- Provide a tool for analyzing stats from past World Cups

## Project Overview
The world cup is coming to North America! If you need to beat your family in bracket competition or just want to put down some parlays, this tool is right for you. This web application has two main purposes: analysis and prediction making.


## Key Features

### Analysis
There are two main pages for the analysis part of the web application - player and team analytics. Player analytics allows you to explore anything from top scorers to those who have made the most appearances off of the bench with so much more inbetween. Team analytics allows for similar viewing but on the team level. Who has won the the most world cups? Which regions tend to perform the best? These are both questions that could be answered using this page!

### Prediction
The prediction tool allows you to select two teams, a stadium, and a temperature and gives you back a prediction of the result of the match! What makes this tool even cooler is the ability to pit teams against each other from different years. How would the 2022 champions Argentina fair against the 2014 champions Germany? Find out using the prediction tool!

## Data Sources

### 1. Fjelstul World Cup Database
Comprehensive collection of CSV files with information about every World Cup. Key information taken from this database includes players, teams, stats, and stadiums used. \
[Link](https://github.com/jfjelstul/worldcup)
### 2. Weather Dataset
NOAA provides climate data and this was used to find an average temperature for the locations of World Cup matches. Temperature is part of the model used for predicting the matches. \
[Link](https://www.ncei.noaa.gov/cdo-web/)

### FIFA Rankings Dataset
This Kaggle dataset provides ranking information for both men's and women's teams. This data goes back to 1992 for men and 2003 for women. The prediction model uses an average ranking calculated using these values. \
[Link - Mens](https://www.kaggle.com/datasets/cashncarry/fifaworldranking/code) \
[Link - Womens](https://www.kaggle.com/datasets/cashncarry/fifa-world-ranking-women)
## File Structure
```
docs
    |---- Diagrams
    |---- Functional Spec
    |---- Technology Review
notebooks
world_cup_26_predictions
    |---- data
    |---- Pages
    |---- player_analytics
    |---- predictions
    |---- tests
    |---- Homepage.py
environment.yml
examples
README.md
```

## Steps for use
- Clone the repository: `git clone https://github.com/KPfeil25/world-cup-26-predictions.git`
- Change into the repository: `cd world-cup-26-predictions`
- Create the environment: `conda env create -f environment.yml`
- Activate the environment: `conda activate world-cup-predictions-env`
- Run the application: `streamlit run world_cup_26_predictions/Homepage.py`
