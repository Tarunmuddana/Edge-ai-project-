"""
AQI Calculator Module
Computes Air Quality Index from pollutant concentrations.
Deterministic, fast, edge-appropriate logic.
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class AQICategory(Enum):
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


@dataclass
class AQIResult:
    aqi: float
    category: AQICategory
    dominant_pollutant: str
    alert_required: bool
    
    def to_dict(self):
        return {
            'aqi': self.aqi,
            'category': self.category.value,
            'dominant_pollutant': self.dominant_pollutant,
            'alert_required': self.alert_required
        }


# EPA Breakpoints for AQI calculation (simplified)
# Format: (C_low, C_high, I_low, I_high)
AQI_BREAKPOINTS = {
    'CO': [  # mg/m³
        (0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ],
    'NO2': [  # ppb -> µg/m³ approximation
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 2049, 301, 500),
    ],
    'O3': [  # ppb (8-hour average)
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
    ],
    'PM2.5': [  # µg/m³
        (0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ],
}


def calculate_sub_aqi(concentration: float, pollutant: str) -> float:
    """
    Calculate sub-index AQI for a single pollutant using EPA formula.
    
    AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
    """
    if pollutant not in AQI_BREAKPOINTS:
        return 0.0
    
    breakpoints = AQI_BREAKPOINTS[pollutant]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
            return round(aqi, 1)
    
    # If above all breakpoints, return max
    if concentration > breakpoints[-1][1]:
        return 500.0
    
    return 0.0


def get_aqi_category(aqi: float) -> AQICategory:
    """Classify AQI value into category."""
    if aqi <= 50:
        return AQICategory.GOOD
    elif aqi <= 100:
        return AQICategory.MODERATE
    elif aqi <= 150:
        return AQICategory.UNHEALTHY_SENSITIVE
    elif aqi <= 200:
        return AQICategory.UNHEALTHY
    elif aqi <= 300:
        return AQICategory.VERY_UNHEALTHY
    else:
        return AQICategory.HAZARDOUS


def compute_aqi(co: float = 0, no2: float = 0, o3: float = 0, pm25: float = 0) -> AQIResult:
    """
    Compute overall AQI from multiple pollutant concentrations.
    
    The overall AQI is the maximum of all sub-indices.
    This is the EPA standard approach.
    
    Args:
        co: Carbon Monoxide concentration (mg/m³)
        no2: Nitrogen Dioxide concentration (µg/m³)
        o3: Ozone concentration (ppb)
        pm25: PM2.5 concentration (µg/m³)
    
    Returns:
        AQIResult with computed AQI, category, and alert status
    """
    sub_indices = {
        'CO': calculate_sub_aqi(co, 'CO'),
        'NO2': calculate_sub_aqi(no2, 'NO2'),
        'O3': calculate_sub_aqi(o3, 'O3'),
        'PM2.5': calculate_sub_aqi(pm25, 'PM2.5'),
    }
    
    # Overall AQI is the maximum sub-index
    overall_aqi = max(sub_indices.values())
    dominant = max(sub_indices, key=sub_indices.get)
    category = get_aqi_category(overall_aqi)
    
    # Alert required if AQI > 100 (unhealthy for sensitive groups or worse)
    alert_required = overall_aqi > 100
    
    return AQIResult(
        aqi=overall_aqi,
        category=category,
        dominant_pollutant=dominant,
        alert_required=alert_required
    )


def compute_simple_aqi(co: float = 0, no2: float = 0, o3: float = 0) -> Tuple[float, str, bool]:
    """
    Simplified AQI computation for edge devices.
    Returns (aqi_value, category_string, alert_needed)
    """
    result = compute_aqi(co=co, no2=no2, o3=o3)
    return result.aqi, result.category.value, result.alert_required


if __name__ == "__main__":
    # Test the calculator
    result = compute_aqi(co=8.5, no2=120, o3=60, pm25=45)
    print(f"AQI: {result.aqi}")
    print(f"Category: {result.category.value}")
    print(f"Dominant Pollutant: {result.dominant_pollutant}")
    print(f"Alert Required: {result.alert_required}")
