"""
Main execution script for Edge-Based Air Quality System.
Runs a simulation and generates a report without GUI.
Useful for automated testing and result generation.
"""

import time
import os
import pandas as pd
from src.sensor_stream import SensorStream, generate_synthetic_data
from src.edge_node import EdgeNode
from src.cloud_node import CloudNode

def run_simulation(n_readings=50, data_path='data/air_quality.csv'):
    print("="*60)
    print(" EDGE-BASED AIR QUALITY EARLY WARNING SYSTEM - SIMULATION")
    print("="*60)
    
    # 1. Setup
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if not os.path.exists(data_path):
        print(f"[SETUP] Generating synthetic data at {data_path}...")
        generate_synthetic_data(save_path=data_path)
    
    print("[SETUP] Initializing Nodes...")
    edge = EdgeNode(alert_threshold=100, simulated_delay_ms=50)
    cloud = CloudNode(alert_threshold=100, network_delay_ms=2000)
    stream = SensorStream(data_path, delay=0.05) # Fast simulation
    
    results = []
    
    print(f"[RUN] Processing {n_readings} readings...")
    
    # 2. Processing Loop
    for i, reading in enumerate(stream.stream_fast(max_readings=n_readings)):
        # Edge
        edge_res = edge.process_reading(reading)
        
        # Cloud
        cloud_res = cloud.process_reading(reading)
        
        results.append({
            'Reading_ID': i+1,
            'Pollutant_CO': reading['CO'],
            'AQI': edge_res.aqi_result.aqi,
            'Category': edge_res.aqi_result.category.value,
            'Edge_Latency_ms': edge_res.processing_time_ms,
            'Cloud_Latency_ms': cloud_res.total_latency_ms,
            'Alert': "YES" if edge_res.alert_triggered else "NO"
        })
        
        # progress bar
        if i % 10 == 0:
            print(f"  -> Processed {i}/{n_readings}...")

    print("[DONE] Simulation finished.")
    
    # 3. Analysis
    df = pd.DataFrame(results)
    
    avg_edge = df['Edge_Latency_ms'].mean()
    avg_cloud = df['Cloud_Latency_ms'].mean()
    improvement = avg_cloud / avg_edge if avg_edge > 0 else 0
    alerts_triggered = df[df['Alert'] == "YES"].shape[0]
    
    print("\n" + "-"*30)
    print(" FINAL RESULTS SUMMARY")
    print("-"*(30))
    print(f"Total Readings:    {n_readings}")
    print(f"Alerts Triggered:  {alerts_triggered}")
    print(f"Avg Edge Latency:  {avg_edge:.2f} ms")
    print(f"Avg Cloud Latency: {avg_cloud:.2f} ms")
    print(f"Speedup Factor:    {improvement:.1f}x FASTER at Edge")
    print("-"*(30))
    
    # Save results
    if not os.path.exists('reports'):
        os.makedirs('reports')
    df.to_csv('reports/simulation_results.csv', index=False)
    print("Results saved to reports/simulation_results.csv")

if __name__ == "__main__":
    run_simulation()
