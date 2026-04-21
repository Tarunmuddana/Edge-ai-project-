"""
Edge Inference Engine.
Loads the trained ML model and runs predictions locally.
"""

import joblib
import pandas as pd
import numpy as np
import os
from dataclasses import dataclass

MODEL_PATH = "models/edge_forecast_model.pkl"

@dataclass
class PredictionResult:
    predicted_aqi: float
    time_to_hazard_min: int
    confidence_score: float

class EdgePredictor:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Load model from disk."""
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print("Edge Inference Engine: Model Loaded.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
        else:
            print("Edge Inference Engine: No model found.")

    def predict(self, reading: dict) -> PredictionResult:
        """
        Run inference on the edge device.
        Predicts AQI for the next time step.
        """
        if self.model is None:
            return PredictionResult(0, 0, 0.0)
            
        # Prepare feature vector (Must match training order)
        # ['CO(GT)', 'NO2(GT)', 'PT08.S5(O3)', 'T', 'RH']
        features = np.array([[
            reading.get('CO', 0),
            reading.get('NO2', 0),
            reading.get('O3_sensor', reading.get('O3', 0) * 20), # Revert scaling if needed or map correctly
            reading.get('Temperature', 20),
            reading.get('Humidity', 50)
        ]])
        
        try:
            pred_aqi = self.model.predict(features)[0]
            
            # Simple heuristic for "Time to Hazard" if trend is rising
            current_aqi = reading.get('AQI', 0)
            if pred_aqi > current_aqi and pred_aqi > 100:
                time_to_hazard = 45 # Simulated prediction: "In 45 mins"
            else:
                time_to_hazard = 0
                
            return PredictionResult(
                predicted_aqi=pred_aqi,
                time_to_hazard_min=time_to_hazard,
                confidence_score=0.85 # Mock confidence for Random Forest
            )
        except Exception as e:
            print(f"Inference error: {e}")
            return PredictionResult(0, 0, 0.0)
