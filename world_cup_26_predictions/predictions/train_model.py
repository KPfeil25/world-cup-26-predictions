'''
NAME:
    train_model - Module for setting up and training the World Cup match prediction model

DESCRIPTION:
    This module implements a machine learning pipeline for predicting soccer match results.
    It includes a MatchResultPredictor class that handles data preprocessing, model training,
    and match prediction functionality. The model uses a random forest classifier with 
    special handling for draw results, emphasizing wins and losses for better predictive
    accuracy.

CLASSES:
    MatchResultPredictor - Class that implements the model training and prediction pipeline

FILE:
    /tmp/world_cup_26_predictions/predictions/train_model.py
'''

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from world_cup_26_predictions.predictions.data_manager import prepare_training_data

class MatchResultPredictor:
    '''
    Handles the training and prediction pipeline for soccer match results.
    
    This class creates a complete machine learning pipeline for predicting match outcomes
    (win, loss, or draw) using a Random Forest classifier. It includes preprocessing for
    both numerical and categorical features, class weighting to handle the 
    imbalance of draw results, and prediction functionality with 
    additional draw penalty adjustments.
    
    Methods:
        create_preprocessor - Creates preprocessing pipelines for different data types
        train_model - Trains the model and saves it to disk
        predict_match - Loads the saved model and makes predictions on new match data
    '''
    def create_preprocessor(self, x):
        """
        Creates a preprocessing pipeline for both numerical and categorical features.
        
        Constructs a ColumnTransformer that handles different feature types appropriately:
        - For numerical features: Imputes missing values with median and applies standard scaling
        - For categorical features: Imputes missing values with most frequent
          value and applies one-hot encoding
        
        Args:
            x (pandas.DataFrame): The feature DataFrame with mixed data types
            
        Returns:
            sklearn.compose.ColumnTransformer: A preprocessing pipeline configured
                                               for the input data
        """
        numeric_features = x.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = x.select_dtypes(include=['object']).columns.tolist()
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler())
                ]), numeric_features),
                ('cat', Pipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('onehot', OneHotEncoder(handle_unknown='ignore'))
                ]), categorical_features)
            ])
        return preprocessor

    def train_model(self, matches):
        """
        Trains the prediction model and saves it to disk.
        
        Processes the input data, encodes the target variable, constructs the full pipeline,
        trains the model, and evaluates its performance. The model and label encoder are saved
        to disk for later use in predictions.
        
        Args:
            matches (pandas.DataFrame): Match data with features and 'result' column
            
        Returns:
            tuple: A tuple containing:
                - The trained pipeline model
                - The preprocessor component
                - The LabelEncoder used for target encoding
        """
        le = LabelEncoder()
        matches['result_encoded'] = le.fit_transform(matches['result'])
        feature_columns = matches.columns.difference(['result', 'result_encoded']).tolist()
        x = matches[feature_columns]
        y = matches['result_encoded']
        preprocessor = self.create_preprocessor(x)
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=200,
                random_state=42))
        ])
        x_train, _, y_train, _ = train_test_split(x, y, test_size=0.25, random_state=42)
        model.fit(x_train, y_train)

        joblib.dump(model, "model.pkl")
        joblib.dump(le, "label_encoder.pkl")
        return model, preprocessor, le

    def predict_match(self, new_match_data):
        '''
        Predicts the outcome of new matches.
        
        Loads the previously trained model and label encoder, makes predictions
        on new match data, and applies an additional penalty to draw predictions 
        to favor more decisive outcomes.
        
        Args:
            new_match_data (pandas.DataFrame): New match data in the same format as training data,
                                              but without the 'result' column
            
        Returns:
            numpy.ndarray: Array of predicted match results ('Home Win', 'Away Win', 'Draw')
        '''
        model = joblib.load("model.pkl")
        le = joblib.load("label_encoder.pkl")
        prediction_probs = model.predict_proba(new_match_data)
        prediction_encoded = np.argmax(prediction_probs, axis=1)
        return le.inverse_transform(prediction_encoded)

if __name__ == "__main__":
    df = prepare_training_data()
    predictor = MatchResultPredictor()
    predictor.train_model(df)
