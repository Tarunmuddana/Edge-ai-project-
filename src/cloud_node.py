"""
Cloud Node Module
Simulates cloud computing processing with network latency.
Data is sent to cloud, processed centrally, and results returned.
"""

import time
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import random

from .aqi_calculator import compute_aqi, AQIResult


@dataclass
class CloudProcessingResult:
    """Result of cloud node processing."""
    reading_id: int
    timestamp: str
    aqi_result: AQIResult
    network_delay_ms: float
    processing_time_ms: float
    total_latency_ms: float
    alert_triggered: bool
    processing_location: str = "CLOUD"
    
    def to_dict(self):
        return {
            'reading_id': self.reading_id,
            'timestamp': self.timestamp,
            'aqi': self.aqi_result.aqi,
            'category': self.aqi_result.category.value,
            'dominant_pollutant': self.aqi_result.dominant_pollutant,
            'alert_triggered': self.alert_triggered,
            'network_delay_ms': round(self.network_delay_ms, 2),
            'processing_time_ms': round(self.processing_time_ms, 2),
            'total_latency_ms': round(self.total_latency_ms, 2),
            'processing_location': self.processing_location,
        }


class CloudNode:
    """
    Cloud Computing Node Simulator.
    
    Characteristics:
    - High latency due to network round-trip
    - Centralized processing
    - Batch processing capability
    - Long-term storage
    """
    
    def __init__(
        self,
        alert_threshold: float = 100.0,
        network_delay_ms: float = 1500.0,
        network_jitter_ms: float = 500.0,
        processing_delay_ms: float = 500.0,
    ):
        """
        Initialize cloud node.
        
        Args:
            alert_threshold: AQI threshold for triggering alerts
            network_delay_ms: Base network round-trip delay (default 1500ms)
            network_jitter_ms: Random variation in network delay (default 500ms)
            processing_delay_ms: Cloud processing overhead (default 500ms)
        """
        self.alert_threshold = alert_threshold
        self.network_delay_ms = network_delay_ms
        self.network_jitter_ms = network_jitter_ms
        self.processing_delay_ms = processing_delay_ms
        self.processing_history: List[CloudProcessingResult] = []
        self.alert_count = 0
        self.total_readings = 0
        self.storage: List[Dict] = []  # Simulated cloud storage
        
    def _simulate_network_delay(self) -> float:
        """Simulate realistic network delay with jitter."""
        jitter = random.uniform(-self.network_jitter_ms, self.network_jitter_ms)
        delay = max(100, self.network_delay_ms + jitter)  # Minimum 100ms
        return delay
        
    def process_reading(self, reading: Dict) -> CloudProcessingResult:
        """
        Process a single sensor reading via cloud.
        
        Steps:
        1. Simulate network upload delay
        2. Cloud processing
        3. Simulate network download delay
        4. Return result
        
        Args:
            reading: Dictionary with pollutant values
            
        Returns:
            CloudProcessingResult with computed values and timing
        """
        start_time = time.perf_counter()
        
        # Simulate network delay (upload)
        upload_delay = self._simulate_network_delay() / 2
        time.sleep(upload_delay / 1000)
        
        # Simulate cloud processing
        time.sleep(self.processing_delay_ms / 1000)
        
        # Compute AQI in the cloud
        aqi_result = compute_aqi(
            co=reading.get('CO', 0),
            no2=reading.get('NO2', 0),
            o3=reading.get('O3', 0),
            pm25=reading.get('PM25', 0)
        )
        
        # Store in cloud storage
        self._store_reading(reading, aqi_result)
        
        # Simulate network delay (download)
        download_delay = self._simulate_network_delay() / 2
        time.sleep(download_delay / 1000)
        
        # Calculate total time
        end_time = time.perf_counter()
        total_latency_ms = (end_time - start_time) * 1000
        network_delay_total = upload_delay + download_delay
        
        # Make decision
        alert_triggered = aqi_result.aqi > self.alert_threshold
        
        # Create result
        result = CloudProcessingResult(
            reading_id=reading.get('reading_id', 0),
            timestamp=reading.get('timestamp', datetime.now().isoformat()),
            aqi_result=aqi_result,
            network_delay_ms=network_delay_total,
            processing_time_ms=self.processing_delay_ms,
            total_latency_ms=total_latency_ms,
            alert_triggered=alert_triggered,
        )
        
        # Update statistics
        self.total_readings += 1
        if alert_triggered:
            self.alert_count += 1
        
        self.processing_history.append(result)
        
        return result
    
    def _store_reading(self, reading: Dict, aqi_result: AQIResult):
        """Store reading in cloud storage for historical analysis."""
        self.storage.append({
            'reading': reading,
            'aqi': aqi_result.aqi,
            'category': aqi_result.category.value,
            'stored_at': datetime.now().isoformat(),
        })
    
    def process_batch(self, readings: List[Dict]) -> List[CloudProcessingResult]:
        """
        Process multiple readings in batch.
        More efficient than individual processing but still has network delay.
        """
        results = []
        start_time = time.perf_counter()
        
        # Single network round-trip for batch
        network_delay = self._simulate_network_delay()
        time.sleep(network_delay / 1000)
        
        # Process all readings
        for reading in readings:
            aqi_result = compute_aqi(
                co=reading.get('CO', 0),
                no2=reading.get('NO2', 0),
                o3=reading.get('O3', 0),
                pm25=reading.get('PM25', 0)
            )
            
            alert_triggered = aqi_result.aqi > self.alert_threshold
            
            result = CloudProcessingResult(
                reading_id=reading.get('reading_id', 0),
                timestamp=reading.get('timestamp', datetime.now().isoformat()),
                aqi_result=aqi_result,
                network_delay_ms=network_delay,
                processing_time_ms=self.processing_delay_ms,
                total_latency_ms=0,  # Will be updated below
                alert_triggered=alert_triggered,
            )
            results.append(result)
            
            self.total_readings += 1
            if alert_triggered:
                self.alert_count += 1
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        
        # Update latency for all results
        for result in results:
            result.total_latency_ms = total_time
        
        self.processing_history.extend(results)
        
        return results
    
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
        
        latencies = [r.total_latency_ms for r in self.processing_history]
        
        return {
            'total_readings': self.total_readings,
            'alert_count': self.alert_count,
            'alert_rate': self.alert_count / self.total_readings if self.total_readings > 0 else 0,
            'avg_latency_ms': sum(latencies) / len(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'avg_network_delay_ms': sum(r.network_delay_ms for r in self.processing_history) / len(self.processing_history),
            'processing_location': 'CLOUD',
            'storage_size': len(self.storage),
        }
    
    def get_historical_data(self, limit: int = 100) -> List[Dict]:
        """Get historical data from cloud storage."""
        return self.storage[-limit:]
    
    def reset(self):
        """Reset the cloud node state."""
        self.processing_history = []
        self.alert_count = 0
        self.total_readings = 0
        self.storage = []


if __name__ == "__main__":
    # Test cloud node
    cloud = CloudNode(
        alert_threshold=100,
        network_delay_ms=2000,
        network_jitter_ms=500,
        processing_delay_ms=500,
    )
    
    # Test readings
    test_readings = [
        {'CO': 2.0, 'NO2': 50, 'O3': 40, 'reading_id': 1, 'timestamp': '2024-01-01 10:00'},
        {'CO': 8.0, 'NO2': 120, 'O3': 80, 'reading_id': 2, 'timestamp': '2024-01-01 10:01'},
        {'CO': 12.0, 'NO2': 200, 'O3': 100, 'reading_id': 3, 'timestamp': '2024-01-01 10:02'},
    ]
    
    for reading in test_readings:
        result = cloud.process_reading(reading)
        print(f"Reading {result.reading_id}: AQI={result.aqi_result.aqi:.1f}, "
              f"Alert={result.alert_triggered}, Latency={result.total_latency_ms:.1f}ms")
    
    print("\nStatistics:", cloud.get_statistics())
