"""
Standalone script to train and save the Edge AI model.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Constants for AQI calculation (from aqi_calculator.py)
CO_BREAKPOINTS = [
    (0.0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150),
    (12.5, 15.4, 151, 200), (15.5, 30.4, 201, 300), (30.5, 40.4, 301, 400),
    (40.5, 50.4, 401, 500)
]

def compute_sub_index(concentration, breakpoints):
    """Calculate AQI sub-index for a pollutant."""
    if concentration < 0:
        concentration = 0
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= concentration <= bp_hi:
            return ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (concentration - bp_lo) + aqi_lo
    return 500  # Max AQI if out of range

def generate_synthetic_data(n_samples=5000):
    """Generate synthetic air quality data."""
    np.random.seed(42)
    
    # Time series with some correlation
    hours = np.arange(n_samples)
    daily_cycle = np.sin(2 * np.pi * hours / 24)
    
    # Generate correlated pollutants
    co = np.clip(2.0 + 3.0 * daily_cycle + np.random.randn(n_samples) * 1.5, 0.1, 20)
    no2 = np.clip(50 + 30 * daily_cycle + np.random.randn(n_samples) * 15, 5, 200)
    o3_sensor = np.clip(1000 + 500 * (-daily_cycle) + np.random.randn(n_samples) * 100, 100, 2500)
    temp = 20 + 10 * daily_cycle + np.random.randn(n_samples) * 3
    humidity = 50 - 20 * daily_cycle + np.random.randn(n_samples) * 10
    
    df = pd.DataFrame({
        'CO(GT)': co,
        'NO2(GT)': no2,
        'PT08.S5(O3)': o3_sensor,
        'T': temp,
        'RH': humidity
    })
    
    return df

def prepare_training_data(n_samples=5000):
    """Generate and prepare data for training."""
    print("Generating synthetic training data...")
    df = generate_synthetic_data(n_samples)
    
    # Calculate AQI for each row (simplified - using CO as primary)
    print("Computing AQI ground truth...")
    aqi_values = []
    for _, row in df.iterrows():
        # Simplified AQI using CO
        aqi = compute_sub_index(row['CO(GT)'], CO_BREAKPOINTS)
        aqi_values.append(aqi)
    
    df['Current_AQI'] = aqi_values
    
    # Create Targets: Shift AQI by -1 to predict NEXT step AQI
    df['Target_AQI'] = df['Current_AQI'].shift(-1)
    
    # Drop last row (NaN target)
    df = df.dropna()
    
    # Features
    feature_cols = ['CO(GT)', 'NO2(GT)', 'PT08.S5(O3)', 'T', 'RH']
    
    X = df[feature_cols]
    y = df['Target_AQI']
    
    return X, y

def train_model():
    """Train and save the Edge AI model."""
    MODEL_PATH = "models/edge_forecast_model.pkl"
    
    if not os.path.exists('models'):
        os.makedirs('models')
        
    X, y = prepare_training_data()
    
    print(f"Training data shape: X={X.shape}, y={y.shape}")
    print("Training Edge AI Model (Random Forest)...")
    
    # Random Forest with limited depth for edge efficiency
    model = RandomForestRegressor(
        n_estimators=50, 
        max_depth=10, 
        random_state=42, 
        n_jobs=-1
    )
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    
    print(f"Model Trained Successfully!")
    print(f"  - MSE: {mse:.2f}")
    print(f"  - R2 Score: {r2:.2f}")
    
    # Save
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    
    return model

if __name__ == "__main__":
    train_model()
