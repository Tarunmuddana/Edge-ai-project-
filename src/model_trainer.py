"""
Edge AI Model Trainer.
Trains a lightweight Regression model to predict future AQI.

Goal: Predict AQI at (t+1) based on features at (t).
Features: [CO, NO2, O3, Temperature, Humidity]
Target: AQI_next
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from .sensor_stream import generate_synthetic_data
from .aqi_calculator import compute_aqi

MODEL_PATH = "models/edge_forecast_model.pkl"

def prepare_training_data(n_samples=5000):
    """Generate and prepare data for training."""
    print("Generating synthetic training data...")
    df = generate_synthetic_data(n_samples, save_path=None)
    
    # Calculate AQI for each row to be the target
    print("Computing AQI ground truth...")
    aqi_values = []
    for _, row in df.iterrows():
        res = compute_aqi(
            co=row['CO(GT)'], 
            no2=row['NO2(GT)'], 
            o3=row['PT08.S5(O3)']/20,  # Scaling as per stream logic
            pm25=0
        )
        aqi_values.append(res.aqi)
    
    df['Current_AQI'] = aqi_values
    
    # Create Targets: Shift AQI by -1 to predict NEXT step AQI
    df['Target_AQI'] = df['Current_AQI'].shift(-1)
    
    # Drop last row (NaN target)
    df = df.dropna()
    
    # Features (Simulating sensors available at edge)
    feature_cols = ['CO(GT)', 'NO2(GT)', 'PT08.S5(O3)', 'T', 'RH']
    
    X = df[feature_cols]
    y = df['Target_AQI']
    
    return X, y

def train_model():
    """Train and save the Edge AI model."""
    if not os.path.exists('models'):
        os.makedirs('models')
        
    X, y = prepare_training_data()
    
    print("Training Edge AI Model (Random Forest)...")
    # Using Random Forest for non-linear relationships, but limiting depth for "Edge" efficiency
    model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    
    print(f"Model Trained. MSE: {mse:.2f}, R2: {r2:.2f}")
    
    # Save
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

if __name__ == "__main__":
    train_model()
