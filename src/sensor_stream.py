"""
Sensor Stream Module
Simulates real-time sensor data streaming from CSV.
Each row is treated as a timestamped sensor reading.
"""

import pandas as pd
import numpy as np
import time
from typing import Generator, Dict, Optional
from pathlib import Path


class SensorStream:
    """
    Simulates real-time sensor data streaming.
    Reads from CSV and yields rows with configurable delay.
    """
    
    def __init__(self, data_path: str, delay: float = 0.5):
        """
        Initialize sensor stream.
        
        Args:
            data_path: Path to CSV file with sensor data
            delay: Delay between readings in seconds (default 0.5s)
        """
        self.data_path = Path(data_path)
        self.delay = delay
        self.df = None
        self.current_index = 0
        
    def load_data(self) -> bool:
        """Load and preprocess the dataset."""
        try:
            # UCI Air Quality dataset uses semicolon separator
            self.df = pd.read_csv(self.data_path, sep=';', decimal=',')
            
            # Clean column names
            self.df.columns = self.df.columns.str.strip()
            
            # Handle missing values (marked as -200 in UCI dataset)
            self.df = self.df.replace(-200, np.nan)
            self.df = self.df.fillna(method='ffill').fillna(method='bfill')
            
            self.current_index = 0
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Map dataset columns to standard pollutant names.
        UCI Air Quality dataset specific.
        """
        return {
            'CO(GT)': 'CO',
            'PT08.S1(CO)': 'CO_sensor',
            'NMHC(GT)': 'NMHC',
            'C6H6(GT)': 'Benzene',
            'PT08.S2(NMHC)': 'NMHC_sensor',
            'NOx(GT)': 'NOx',
            'PT08.S3(NOx)': 'NOx_sensor',
            'NO2(GT)': 'NO2',
            'PT08.S4(NO2)': 'NO2_sensor',
            'PT08.S5(O3)': 'O3_sensor',
            'T': 'Temperature',
            'RH': 'Humidity',
            'AH': 'Absolute_Humidity',
        }
    
    def stream(self, max_readings: Optional[int] = None) -> Generator[Dict, None, None]:
        """
        Stream sensor readings one at a time.
        
        Args:
            max_readings: Maximum number of readings to stream (None = all)
        
        Yields:
            Dictionary with pollutant values and timestamp
        """
        if self.df is None:
            if not self.load_data():
                return
        
        column_map = self.get_column_mapping()
        readings_count = 0
        
        for idx, row in self.df.iterrows():
            if max_readings and readings_count >= max_readings:
                break
            
            # Extract relevant pollutant values
            reading = {
                'timestamp': f"{row.get('Date', 'N/A')} {row.get('Time', 'N/A')}",
                'CO': float(row.get('CO(GT)', 0)),
                'NO2': float(row.get('NO2(GT)', 0)),
                'NOx': float(row.get('NOx(GT)', 0)),
                'O3_sensor': float(row.get('PT08.S5(O3)', 0)),
                'Temperature': float(row.get('T', 0)),
                'Humidity': float(row.get('RH', 0)),
                'reading_id': idx,
            }
            
            # Scale O3 sensor reading to approximate ppb
            # PT08.S5 is a metal oxide sensor, values need scaling
            reading['O3'] = reading['O3_sensor'] / 20  # Approximate scaling
            
            yield reading
            readings_count += 1
            
            # Simulate real-time with delay
            if self.delay > 0:
                time.sleep(self.delay)
    
    def stream_fast(self, max_readings: Optional[int] = None) -> Generator[Dict, None, None]:
        """Stream without delays for batch processing."""
        original_delay = self.delay
        self.delay = 0
        yield from self.stream(max_readings)
        self.delay = original_delay
    
    def get_sample_reading(self) -> Dict:
        """Get a single sample reading for testing."""
        if self.df is None:
            self.load_data()
        
        if self.df is not None and len(self.df) > 0:
            for reading in self.stream_fast(max_readings=1):
                return reading
        
        # Return synthetic data if no file available
        return {
            'timestamp': '2024-01-01 12:00:00',
            'CO': 2.5,
            'NO2': 85,
            'NOx': 120,
            'O3': 55,
            'Temperature': 22.0,
            'Humidity': 45.0,
            'reading_id': 0,
        }


def generate_synthetic_data(n_samples: int = 1000, save_path: str = None) -> pd.DataFrame:
    """
    Generate synthetic air quality data for testing.
    Mimics realistic urban pollution patterns.
    """
    np.random.seed(42)
    
    # Time of day affects pollution (rush hours = higher)
    hours = np.arange(n_samples) % 24
    rush_hour_factor = 1 + 0.5 * (np.sin(2 * np.pi * hours / 24 - np.pi/2) + 1)
    
    # Base pollution levels with daily variation
    co_base = 3.0 + 2.0 * rush_hour_factor + np.random.normal(0, 0.5, n_samples)
    no2_base = 50 + 30 * rush_hour_factor + np.random.normal(0, 10, n_samples)
    o3_base = 40 + 20 * np.sin(2 * np.pi * hours / 24) + np.random.normal(0, 8, n_samples)
    
    # Add some pollution spikes
    spike_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    co_base[spike_indices] *= 2.5
    no2_base[spike_indices] *= 2.0
    
    # Create dataframe in UCI format
    df = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=n_samples, freq='h').strftime('%d/%m/%Y'),
        'Time': pd.date_range(start='2024-01-01', periods=n_samples, freq='h').strftime('%H.%M.%S'),
        'CO(GT)': np.clip(co_base, 0.5, 15).round(1),
        'NO2(GT)': np.clip(no2_base, 10, 400).round(0),
        'NOx(GT)': np.clip(no2_base * 1.5, 20, 600).round(0),
        'PT08.S5(O3)': np.clip(o3_base * 20, 500, 2500).round(0),  # Sensor units
        'T': (20 + 5 * np.sin(2 * np.pi * hours / 24) + np.random.normal(0, 2, n_samples)).round(1),
        'RH': (50 + 15 * np.cos(2 * np.pi * hours / 24) + np.random.normal(0, 5, n_samples)).round(1),
        'AH': np.random.uniform(0.5, 1.5, n_samples).round(2),
    })
    
    if save_path:
        df.to_csv(save_path, sep=';', index=False)
        print(f"Synthetic data saved to {save_path}")
    
    return df


if __name__ == "__main__":
    # Generate test data
    generate_synthetic_data(500, 'data/air_quality.csv')
    
    # Test streaming
    stream = SensorStream('data/air_quality.csv', delay=0)
    for i, reading in enumerate(stream.stream_fast(max_readings=5)):
        print(f"Reading {i+1}: CO={reading['CO']:.1f}, NO2={reading['NO2']:.0f}, O3={reading['O3']:.0f}")
