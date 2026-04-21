"""
Edge Node Module
Simulates edge computing processing with low latency.
Decision-making happens locally with minimal delay.
"""

import time
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .aqi_calculator import compute_aqi, AQIResult
from .edge_ai import EdgePredictor, PredictionResult

@dataclass
class EdgeProcessingResult:
    """Result of edge node processing."""
    reading_id: int
    timestamp: str
    aqi_result: AQIResult
    processing_time_ms: float
    alert_triggered: bool
    prediction: PredictionResult = None   # New AI field
    processing_location: str = "EDGE"
    
    def to_dict(self):
        return {
            'reading_id': self.reading_id,
            'timestamp': self.timestamp,
            'aqi': self.aqi_result.aqi,
            'category': self.aqi_result.category.value,
            'dominant_pollutant': self.aqi_result.dominant_pollutant,
            'alert_triggered': self.alert_triggered,
            'processing_time_ms': round(self.processing_time_ms, 2),
            'processing_location': self.processing_location,
        }


class EdgeNode:
    """
    Edge Computing Node Simulator.
    
    Characteristics:
    - Low latency processing (< 100ms)
    - Immediate decision making
    - Threshold-based alerting
    - Local data processing
    """
    
    def __init__(self, alert_threshold: float = 100.0, simulated_delay_ms: float = 50.0):
        """
        Initialize edge node.
        
        Args:
            alert_threshold: AQI threshold for triggering alerts (default 100)
            simulated_delay_ms: Simulated edge processing overhead (default 50ms)
        """
        self.alert_threshold = alert_threshold
        self.simulated_delay_ms = simulated_delay_ms
        self.processing_history: List[EdgeProcessingResult] = []
        self.alert_count = 0
        self.total_readings = 0
        self.ai_engine = EdgePredictor() # Initialize AI
        
    def process_reading(self, reading: Dict) -> EdgeProcessingResult:
        """
        Process a single sensor reading at the edge.
        Now includes AI Inference.
        """
        start_time = time.perf_counter()
        
        # Simulate edge processing delay (memory access, computation)
        time.sleep(self.simulated_delay_ms / 1000)
        
        # 1. Compute AQI (Standard Logic)
        aqi_result = compute_aqi(
            co=reading.get('CO', 0),
            no2=reading.get('NO2', 0),
            o3=reading.get('O3', 0),
            pm25=reading.get('PM25', 0)
        )
        
        # 2. Run AI Prediction (New)
        # We pass the current reading to predict the NEXT state
        ai_reading = reading.copy()
        ai_reading['AQI'] = aqi_result.aqi # Inject computed AQI for trend
        prediction = self.ai_engine.predict(ai_reading)
        
        # Make decision locally
        alert_triggered = aqi_result.aqi > self.alert_threshold
        
        # AI-Enhanced Decision: If prediction is bad, trigger Early Warning?
        # For now, we just log it, but valid logic would be:
        # if prediction.predicted_aqi > self.alert_threshold: warning_triggered = True
        
        # Calculate processing time
        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000
        
        # Create result
        result = EdgeProcessingResult(
            reading_id=reading.get('reading_id', 0),
            timestamp=reading.get('timestamp', datetime.now().isoformat()),
            aqi_result=aqi_result,
            processing_time_ms=processing_time_ms,
            alert_triggered=alert_triggered,
            prediction=prediction
        )
        
        # Update statistics
        self.total_readings += 1
        if alert_triggered:
            self.alert_count += 1
            self._trigger_alert(result)
        
        self.processing_history.append(result)
        
        return result
    
    def _trigger_alert(self, result: EdgeProcessingResult):
        """
        Trigger immediate alert action.
        In production: could trigger alarm, send notification, activate ventilation, etc.
        """
        # In simulation, we just log the alert
        pass
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        if not self.processing_history:
            return {
                'total_readings': 0,
                'alert_count': 0,
                'avg_latency_ms': 0,
                'min_latency_ms': 0,
                'max_latency_ms': 0,
            }
        
        latencies = [r.processing_time_ms for r in self.processing_history]
        
        return {
            'total_readings': self.total_readings,
            'alert_count': self.alert_count,
            'alert_rate': self.alert_count / self.total_readings if self.total_readings > 0 else 0,
            'avg_latency_ms': sum(latencies) / len(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'processing_location': 'EDGE',
        }
    
    def get_recent_alerts(self, n: int = 10) -> List[Dict]:
        """Get the most recent alerts."""
        alerts = [r for r in self.processing_history if r.alert_triggered]
        return [a.to_dict() for a in alerts[-n:]]
    
    def reset(self):
        """Reset the edge node state."""
        self.processing_history = []
        self.alert_count = 0
        self.total_readings = 0


if __name__ == "__main__":
    # Test edge node
    edge = EdgeNode(alert_threshold=100, simulated_delay_ms=50)
    
    # Test readings
    test_readings = [
        {'CO': 2.0, 'NO2': 50, 'O3': 40, 'reading_id': 1, 'timestamp': '2024-01-01 10:00'},
        {'CO': 8.0, 'NO2': 120, 'O3': 80, 'reading_id': 2, 'timestamp': '2024-01-01 10:01'},
        {'CO': 12.0, 'NO2': 200, 'O3': 100, 'reading_id': 3, 'timestamp': '2024-01-01 10:02'},
    ]
    
    for reading in test_readings:
        result = edge.process_reading(reading)
        print(f"Reading {result.reading_id}: AQI={result.aqi_result.aqi:.1f}, "
              f"Alert={result.alert_triggered}, Latency={result.processing_time_ms:.1f}ms")
    
    print("\nStatistics:", edge.get_statistics())
