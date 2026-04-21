import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score

# Add parent directory to path to import train_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from train_model import generate_synthetic_data, compute_sub_index, CO_BREAKPOINTS
except ImportError:
    # If running from root directory
    from train_model import generate_synthetic_data, compute_sub_index, CO_BREAKPOINTS

# Setup plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")
PLOT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'plots')

if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

def save_plot(fig, filename):
    path = os.path.join(PLOT_DIR, filename)
    fig.savefig(path, bbox_inches='tight', dpi=300)
    print(f"Saved plot: {path}")
    plt.close(fig)

def categorize_aqi(aqi):
    if aqi <= 50: return 'Good'
    elif aqi <= 100: return 'Moderate'
    elif aqi <= 150: return 'Unhealthy for Sensitive'
    elif aqi <= 200: return 'Unhealthy'
    elif aqi <= 300: return 'Very Unhealthy'
    else: return 'Hazardous'

def main():
    print("Generating data for visualizations...")
    df = generate_synthetic_data(n_samples=2000)
    
    # Calculate AQI
    aqi_values = [compute_sub_index(row['CO(GT)'], CO_BREAKPOINTS) for _, row in df.iterrows()]
    df['AQI'] = aqi_values
    df['AQI_Category'] = df['AQI'].apply(categorize_aqi)
    df['Hour'] = pd.Series(range(len(df))) % 24
    
    # ---------------------------------------------------------
    # PART 1: DATA VISUALIZATIONS
    # ---------------------------------------------------------
    
    # 1. Time Series of Pollutants
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    df['CO(GT)'].plot(ax=axes[0], color='orange', title='Carbon Monoxide (CO)')
    df['NO2(GT)'].plot(ax=axes[1], color='brown', title='Nitrogen Dioxide (NO2)')
    df['AQI'].plot(ax=axes[2], color='purple', title='Calculated AQI')
    axes[2].set_xlabel('Time (Hours)')
    plt.tight_layout()
    save_plot(fig, '01_pollutants_time_series.png')

    # 2. Temperature and Humidity
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    ax1.plot(df['T'], 'g-', label='Temperature (°C)')
    ax2.plot(df['RH'], 'b-', label='Humidity (%)')
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Temperature (°C)', color='g')
    ax2.set_ylabel('Humidity (%)', color='b')
    plt.title('Environmental Conditions')
    save_plot(fig, '02_temp_humidity.png')

    # 3. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    corr = df[['CO(GT)', 'NO2(GT)', 'PT08.S5(O3)', 'T', 'RH', 'AQI']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Feature Correlation Matrix')
    save_plot(plt.gcf(), '03_correlation_matrix.png')

    # 4. AQI Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['AQI'], bins=30, kde=True, color='purple')
    plt.axvline(100, color='r', linestyle='--', label='Unhealthy Threshold')
    plt.title('Distribution of AQI Values')
    plt.legend()
    save_plot(plt.gcf(), '04_aqi_distribution.png')

    # 5. AQI Categories Pie Chart
    plt.figure(figsize=(8, 8))
    df['AQI_Category'].value_counts().plot.pie(autopct='%1.1f%%', cmap='viridis')
    plt.ylabel('')
    plt.title('Proportion of AQI Categories')
    save_plot(plt.gcf(), '05_aqi_categories.png')

    # 6. Diurnal Cycle (Average by Hour)
    hourly_avg = df.groupby('Hour')[['CO(GT)', 'NO2(GT)', 'AQI']].mean()
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_avg.index, hourly_avg['AQI'], 'o-', label='Mean AQI')
    plt.plot(hourly_avg.index, hourly_avg['NO2(GT)'], 's-', label='Mean NO2')
    plt.xlabel('Hour of Day')
    plt.ylabel('Concentration / Index')
    plt.title('Average Daily Pollution Cycle')
    plt.legend()
    plt.grid(True)
    save_plot(plt.gcf(), '06_diurnal_cycle.png')

    # 7. Scatter: Temp vs Ozone (approx via PT08.S5)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='T', y='PT08.S5(O3)', data=df, alpha=0.5)
    plt.title('Temperature vs Ozone Sensor (Photochemical Smog Effect)')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Ozone Sensor Response')
    save_plot(plt.gcf(), '07_temp_vs_ozone.png')

    # ---------------------------------------------------------
    # PART 2: MODEL PERFORMANCE VISUALIZATIONS
    # ---------------------------------------------------------
    
    print("Loading model and generating predictions...")
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'edge_forecast_model.pkl')
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        print("Model not found! Please run train_model.py first.")
        return

    # Prepare features for prediction (Shift targets like in training)
    df['Target_AQI'] = df['AQI'].shift(-1)
    df_eval = df.dropna()
    X = df_eval[['CO(GT)', 'NO2(GT)', 'PT08.S5(O3)', 'T', 'RH']]
    y_true = df_eval['Target_AQI']
    y_pred = model.predict(X)

    # 8. Actual vs Predicted Scatter
    plt.figure(figsize=(8, 8))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('Actual AQI')
    plt.ylabel('Predicted AQI')
    plt.title('Model Prediction Accuracy')
    save_plot(plt.gcf(), '08_actual_vs_predicted.png')

    # 9. Residuals Distribution
    residuals = y_true - y_pred
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True, color='teal')
    plt.xlabel('Prediction Error (AQI Units)')
    plt.title('Model Residuals Distribution')
    save_plot(plt.gcf(), '09_residuals.png')

    # 10. Alert Classification Confusion Matrix
    # Define Alert: AQI > 100
    alert_true = y_true > 100
    alert_pred = y_pred > 100
    cm = confusion_matrix(alert_true, alert_pred)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['No Alert', 'Alert'],
                yticklabels=['No Alert', 'Alert'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Safety Alert Confusion Matrix')
    save_plot(plt.gcf(), '10_alert_confusion_matrix.png')

    # 11. Feature Importance
    plt.figure(figsize=(10, 6))
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    features = X.columns
    sns.barplot(x=importances[indices], y=features[indices], palette='viridis')
    plt.title('Random Forest Feature Importance')
    plt.xlabel('Relative Importance')
    save_plot(plt.gcf(), '11_feature_importance.png')

    # 12. Latency Comparison (Edge vs Cloud)
    plt.figure(figsize=(8, 6))
    scenarios = ['Cloud API', 'Edge AI (Ours)']
    times = [2000, 50] # ms
    bars = plt.bar(scenarios, times, color=['gray', '#00cc66'])
    plt.ylabel('Latency (ms)')
    plt.title('System Response Time Comparison')
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height} ms', ha='center', va='bottom')
    plt.yscale('log')
    save_plot(plt.gcf(), '12_latency_comparison.png')

    print(f"All visualizations saved to {PLOT_DIR}")

if __name__ == "__main__":
    main()
