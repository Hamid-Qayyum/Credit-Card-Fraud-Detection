import pandas as pd
import joblib
from django.conf import settings
import os 

# Load the trained model

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'templates', 'fraud_detection_model', 'fraud_detection_model.pkl')


model = joblib.load(model_path)

def predict_fraud(dataframe):
    """
    Predicts fraud for the given transaction DataFrame.
    :param dataframe: Pandas DataFrame containing transaction data.
    :return: List of predictions (Fraudulent or Not Fraudulent).
    """
    # Ensure the columns match the training data
    # Replace 'feature_columns' with your actual feature column names
    feature_columns = [ 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount']  # Example columns
    dataframe = dataframe[feature_columns]

    # Make predictions
    predictions = model.predict(dataframe)

    # Convert numeric to readable labels
    return ['Fraudulent' if pred == 1 else 'Not Fraudulent' for pred in predictions]