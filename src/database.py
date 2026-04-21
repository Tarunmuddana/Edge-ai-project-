"""
Database Module for Persistence.
Implements a lightweight SQLite backend to store sensor readings and alerts.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/air_quality.db")

def init_db():
    """Initialize the SQLite database and create tables."""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Readings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            co REAL,
            no2 REAL,
            o3 REAL,
            aqi REAL,
            aqi_category TEXT,
            edge_latency REAL,
            cloud_latency REAL,
            alert_triggered BOOLEAN
        )
    ''')
    
    # Alerts table (for critical events log)
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            aqi REAL,
            message TEXT,
            resolved BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def save_reading(data: dict):
    """Save a single reading to the DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO readings (timestamp, co, no2, o3, aqi, aqi_category, edge_latency, cloud_latency, alert_triggered)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['timestamp'],
        data['CO'],
        data['NO2'],
        data['O3'],
        data['AQI'],
        data['Category'],
        data['Edge_Latency'],
        data['Cloud_Latency'],
        data['Alert'] == "YES"
    ))
    
    # If alert, log it specifically
    if data['Alert'] == "YES":
        c.execute('''
            INSERT INTO alerts (timestamp, aqi, message)
            VALUES (?, ?, ?)
        ''', (data['timestamp'], data['AQI'], f"Hazardous AQI Detected: {data['AQI']:.0f}"))
        
    conn.commit()
    conn.close()

def get_readings(limit=500):
    """Fetch recent readings for analysis."""
    if not DB_PATH.exists():
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM readings ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df.sort_values(by='id') # Return in chronological order for plotting

def get_alerts(limit=50):
    """Fetch recent alerts."""
    if not DB_PATH.exists():
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM alerts ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df

def clear_db():
    """Clear all data (Reset)."""
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM readings")
        c.execute("DELETE FROM alerts")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
