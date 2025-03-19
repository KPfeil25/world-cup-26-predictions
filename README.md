# world-cup-26-predictions
## Status Badge
[![build_test](https://github.com/KPfeil25/world-cup-26-predictions/actions/workflows/build_test.yml/badge.svg?branch=main&event=status)](https://github.com/KPfeil25/world-cup-26-predictions/actions/workflows/build_test.yml)

## Project Type:
The project will be **analytical** in nature and we will also be **creating a tool** to demonstrate the predictive element of our project.

## Question of Interest:
Can we build a predictive model that leverages past world cup data alongside various external factors such as the weather in order to predict future outcomes for the upcoming world cup?

## Project output: Research & Tool (maybe a web app/dashboard)
- Provide weather conditions, teams, stadiums, match statistics, etc. 
- Provide insights into past matches with similar conditions
- Provide predictions on who will win using a ML model

## Project Overview
The world cup is coming to North America! If you need to beat your family in bracket competition or just want to put down some parlays, this tool is right for you. This web application has two main purposes: analysis and prediction making.

# Analysis
There are two main pages for the analysis part of the web application - player and team analytics. Player analytics allows you to explore anything from top scorers to those who have made the most appearances off of the bench with so much more inbetween. Team analytics allows for similar viewing but on the team level. Who has won the the most world cups? Which regions tend to perform the best? These are both questions that could be answered using this page!

# Prediction
The prediction tool allows you to select two teams, a stadium, and a temperature and gives you back a prediction of the result of the match! What makes this tool even cooler is the ability to pit teams against each other from different years. How would the 2022 champions Argentina fair against the 2014 champions Germany? Find out using the prediction tool!

## Data Sources:
- [Fjelstul World Cup Database](https://github.com/jfjelstul/worldcup)
- Weather Dataset (multiple options, [Accuweather](https://www.accuweather.com/en/us/seattle/98104/february-weather/351409) is one)

## Steps for use
- Clone the repository
- `cd` into the repository
- Use `conda env create -f environment.yml` to create the environment
