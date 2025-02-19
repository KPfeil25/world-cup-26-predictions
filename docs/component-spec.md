# Component Spec

## Analytics Components:
### Data Manager
- Loads data from csv files, transforms for analysis purposes
- The data sets/csv
- Cleaned data frame that includes all data from csv
- CSV or data source exists in location that manager can access it 
### Data Generation
- Takes data from manager and creates new summary statistics, time related statistics, any other statistics which may be pertinent to visual development 
- The dataframe output from the data manager
- A new dataframe with new statistics and information which builds upon that in the data manager
- Data manager has returned df 
### Various Analytics Generation Components
- Takes data from data generation df and produces visual or table for consumption by consumer
- Takes in the data frame from data generation function, takes in user input about region, country, year, player of interest
- Visual of user specified filtered data
- User inputs exist (example: a year where we don’t have data for a specific team or small country)

## ML Components: 
### Data Manager
- Loads data from csvs, inputs are csvs, outputs are also csvs
- Data Join Component
- Joins necessary csvs, inputs are csvs, outputs are combined dfs, assumption that csvs are loaded
  
## Feature Engineering
- Uses data loaded by Data Manager to generate new features for model training, inputs are dfs, output is df with new features, assumption that csvs are loaded
### Model Training -> Weight Storage
- Initializes a model and trains it on data, input is df, output is weights
### Model Prediction
- Uses weights stored in github to initialize model and then use inputs to generate prediction, input is weights and input for different features, output is prediction, assumption is that model works and can utilize weights + user inputs are valid
- Input Validation, input is user inputs, output is boolean if input is valid


## Web App Components:
### Setting up User Interface
- Likely a header and tabs for the above components
- Tabs bring user to either the analytics or prediction page
### Connecting to Analytics Components
- Be able to display the created graphics
### Connecting to ML Components
- Be able to display the predictions that are made in the backend
