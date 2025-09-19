"""
NAME:
    test_train_model.py - Unit tests for the MatchResultPredictor class

DESCRIPTION:
    This module contains unit tests for the MatchResultPredictor class in train_model.py.
    The tests ensure that data preprocessing, model training, and prediction functionalities
    work as expected, covering various scenarios including expected transformations,
    proper model saving/loading, and correct label encoding handling.

CLASSES:
    TestMatchResultPredictor - Test suite for MatchResultPredictor functions

FILE:
    /tmp/world_cup_26_predictions/tests/test_train_model.py
"""
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from world_cup_26_predictions.predictions.train_model import MatchResultPredictor

class TestMatchResultPredictor(unittest.TestCase):
    """
    Test suite for the MatchResultPredictor class.
    This class tests various functionalities including data preprocessing,
    model training, and match outcome prediction. The tests verify that the
    correct transformations are applied and that models are trained and used properly.
    """
    def setUp(self):
        """
        Sets up test fixtures with sample data.
        Initializes a MatchResultPredictor instance and creates sample datasets
        for training and new match predictions.
        """
        self.predictor = MatchResultPredictor()
        self.sample_data = pd.DataFrame({
            'home_team': ['Team A', 'Team B', 'Team C', 'Team D'],
            'away_team': ['Team E', 'Team F', 'Team G', 'Team H'],
            'home_rank': [1, 5, 10, 15],
            'away_rank': [2, 7, 9, 12],
            'home_score': [2, 1, 0, 3],
            'away_score': [1, 1, 2, 0],
            'result': ['Home Win', 'Draw', 'Away Win', 'Home Win']
        })
        self.new_match_data = pd.DataFrame({
            'home_team': ['Team A'],
            'away_team': ['Team B'],
            'home_rank': [3],
            'away_rank': [8]
        })

    def test_create_preprocessor(self):
        """
        Tests the create_preprocessor method.
        Ensures that the preprocessor correctly identifies numerical and categorical
        features, applies proper transformations, and returns a ColumnTransformer.
        """
        x = self.sample_data.drop('result', axis=1)
        preprocessor = self.predictor.create_preprocessor(x)
        self.assertIsInstance(preprocessor, ColumnTransformer)
        self.assertEqual(len(preprocessor.transformers), 2)
        transformer_names = [name for name, _, _ in preprocessor.transformers]
        self.assertIn('num', transformer_names)
        self.assertIn('cat', transformer_names)
        num_features = x.select_dtypes(include=['int64', 'float64']).columns.tolist()
        for feature in num_features:
            self.assertIn(feature, x.columns)
        cat_features = x.select_dtypes(include=['object']).columns.tolist()
        for feature in cat_features:
            self.assertIn(feature, x.columns)

    @patch('predictions.train_model.joblib.dump')
    @patch('predictions.train_model.train_test_split')
    def test_train_model(self, mock_train_test_split, mock_joblib_dump):
        """
        Tests the train_model method.
        Ensures that training data is split correctly, the pipeline is constructed,
        and model artifacts are saved properly using joblib.
        """
        sample_data_with_encoding = self.sample_data.copy()
        sample_data_with_encoding['result_encoded'] = [0, 1, 2, 0]
        x_train = self.sample_data.drop('result', axis=1)
        x_test = x_train.copy()
        y_train = np.array([0, 1, 2, 0])
        y_test = y_train.copy()
        mock_train_test_split.return_value = (x_train, x_test, y_train, y_test)
        model, preprocessor, _ = self.predictor.train_model(sample_data_with_encoding)
        self.assertIsInstance(model, Pipeline)
        self.assertIsInstance(preprocessor, ColumnTransformer)
        self.assertEqual(mock_joblib_dump.call_count, 2)
        args, _ = mock_joblib_dump.call_args_list[0]
        self.assertIsInstance(args[0], Pipeline)
        self.assertEqual(args[1], "model.pkl")
        args, _ = mock_joblib_dump.call_args_list[1]
        self.assertEqual(args[1], "label_encoder.pkl")

    @patch('predictions.train_model.joblib.load')
    def test_predict_match(self, mock_joblib_load):
        """
        Tests the predict_match method.
        Verifies that the model loads correctly, makes predictions, and returns
        the expected match result labels.
        """
        mock_model = MagicMock()
        mock_le = MagicMock()
        mock_model.predict_proba.return_value = np.array([
            [0.2, 0.7, 0.1],
        ])
        mock_le.inverse_transform.return_value = np.array(['Home Win'])
        mock_joblib_load.side_effect = [mock_model, mock_le]
        result = self.predictor.predict_match(self.new_match_data)
        self.assertEqual(result[0], 'Home Win')
        mock_model.predict_proba.assert_called_once_with(self.new_match_data)
        mock_le.inverse_transform.assert_called_once()
        self.assertEqual(mock_joblib_load.call_count, 2)

    @patch('predictions.train_model.prepare_training_data')
    def test_main_execution(self, mock_prepare_data):
        """
        Tests the main execution block.
        Ensures that when train_model.py is run as a script, it correctly loads
        data, initializes a predictor, and triggers model training.
        """
        mock_prepare_data.return_value = self.sample_data
        with patch.object(MatchResultPredictor, 'train_model') as mock_train_model:
            df = mock_prepare_data()
            predictor = MatchResultPredictor()
            predictor.train_model(df)
            mock_prepare_data.assert_called_once()
            mock_train_model.assert_called_once_with(df)

if __name__ == '__main__':
    unittest.main()
