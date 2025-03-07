'''
NAME:
    train_model - This module sets up the model

FILE:
    /tmp/world_cup_26_predictions/predictions/train_model.py
'''

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from data_manager import prepare_training_data

class MatchResultPredictor:
    '''
    This class initializes the model training pipeline
    '''
    def create_preprocessor(self, x):
        """
        Create a preprocessing pipeline that handles numerical and categorical data.
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
        Train the model with the preprocessed data.
        """
        le = LabelEncoder()
        matches['result_encoded'] = le.fit_transform(matches['result'])
        feature_columns = matches.columns.difference(['result']).tolist()
        x = matches[feature_columns]
        y = matches['result_encoded']
        preprocessor = self.create_preprocessor(x)
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=200, random_state=42))
        ])
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        print("Model Accuracy:", accuracy_score(y_test, y_pred))
        joblib.dump(model, "model.pkl")
        joblib.dump(preprocessor, "preprocessor.pkl")
        joblib.dump(le, "label_encoder.pkl")
        return model, preprocessor, le

    def predict_match(self, new_match_data):
        '''
        Predict
        '''
        model = joblib.load("model.pkl")
        le = joblib.load("label_encoder.pkl")
        prediction_encoded = model.predict(new_match_data)
        return le.inverse_transform(prediction_encoded)

if __name__ == "__main__":
    df = prepare_training_data()
    predictor = MatchResultPredictor()
    predictor.train_model(df)
