import streamlit as st
import pandas as pd
import time
import os
import sys
import altair as alt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sensor_stream import SensorStream, generate_synthetic_data
from src.edge_node import EdgeNode
from src.cloud_node import CloudNode
from src import database

# Initialize DB
database.init_db()

# Page config
st.set_page_config(
    page_title="EdgeSafe: Industrial Air Quality",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Enterprise" feel
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .metric-card {
        background-color: #ffffff;
        border-left: 5px solid #4CAF50;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-card {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------
# SIDEBAR
# -----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/industry.png", width=60)
    st.title("EdgeSafe Monitor")
    st.markdown("v2.1.0 | Enterprise Edition")
    st.divider()
    
    st.subheader("📡 Device Configuration")
    edge_id = st.text_input("Device ID", "EDGE-NODE-001", disabled=True)
    connection = st.selectbox("Network Backend", ["LoRaWAN (Simulated)", "5G Edge", "WiFi (Cloud Fallback)"])
    
    st.subheader("⚙️ Simulation Params")
    sim_speed = st.slider("Clock Speed (s)", 0.1, 2.0, 0.8)  # Slower default for stability
    threshold = st.number_input("Safety Threshold (AQI)", 50, 500, 100)
    
    st.divider()
    if st.button("🗑️ Clear Database", help="Wipes all historical data"):
        database.clear_db()
        st.success("Database cleared!")
        time.sleep(1)
        st.rerun()

# -----------------
# STATE MANAGEMENT
# -----------------
if 'stream' not in st.session_state:
    data_path = 'data/air_quality.csv'
    if not os.path.exists(data_path):
        os.makedirs('data', exist_ok=True)
        generate_synthetic_data(save_path=data_path)
    st.session_state.data_source = SensorStream(data_path, delay=0)
    st.session_state.stream = st.session_state.data_source.stream()
    
    st.session_state.edge_node = EdgeNode(alert_threshold=threshold, simulated_delay_ms=50)
    st.session_state.cloud_node = CloudNode(alert_threshold=threshold, network_delay_ms=2000)
    st.session_state.is_running = False

# -----------------
# MAIN LAYOUT
# -----------------
st.title("🏭 Edge AI Air Quality System")

tab_live, tab_history, tab_system = st.tabs(["🚀 Live Operations", "📊 Historical Analysis", "🖥️ System Health"])

# === TAB 1: LIVE OPERATIONS ===
with tab_live:
    col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)
    
    # Empty containers for live updates
    with col_kpi_1:
        kpi_aqi = st.empty()
    with col_kpi_2:
        kpi_latency = st.empty()
    with col_kpi_3:
        kpi_status = st.empty()
        
    st.divider()
    
    # Native Streamlit Chart (Flicker-free appending)
    st.subheader("Real-time AQI Stream")
    chart_container = st.empty()
    
    col_logs, col_alerts = st.columns([2, 1])
    with col_logs:
        st.caption("Live Sensor Data Stream")
        log_container = st.empty()
    with col_alerts:
        st.caption("Active Alerts")
        alert_container = st.empty()

    # Control Bar
    start_btn = st.button("▶ Start Monitoring", type="primary", disabled=st.session_state.is_running)
    stop_btn = st.button("⏹ Stop System", disabled=not st.session_state.is_running)

    if start_btn:
        st.session_state.is_running = True
        st.rerun()
    
    if stop_btn:
        st.session_state.is_running = False
        st.rerun()

    # ---------------
    # SIMULATION LOOP
    # ---------------
    if st.session_state.is_running:
        
        # We start with empty dataframes for the charts
        # Using a list to buffer recent data for display
        live_buffer = [] 
        
        try:
            while st.session_state.is_running:
                # 1. Fetch
                reading = next(st.session_state.stream)
                
                # 2. Process
                edge_res = st.session_state.edge_node.process_reading(reading)
                cloud_res = st.session_state.cloud_node.process_reading(reading)
                
                # 3. Save to DB
                packet = {
                    'timestamp': reading['timestamp'],
                    'CO': reading['CO'],
                    'NO2': reading['NO2'],
                    'O3': reading['O3'],
                    'AQI': edge_res.aqi_result.aqi,
                    'Category': edge_res.aqi_result.category.value,
                    'Edge_Latency': edge_res.processing_time_ms,
                    'Cloud_Latency': cloud_res.total_latency_ms,
                    'Alert': "YES" if edge_res.alert_triggered else "NO",
                    'Predicted_AQI': edge_res.prediction.predicted_aqi if edge_res.prediction else 0
                }
                database.save_reading(packet)
                live_buffer.append(packet)
                if len(live_buffer) > 50: live_buffer.pop(0) # Keep UI buffer small
                
                # 4. Update UI Elements (No Rerun!)
                
                # KPIs
                kpi_aqi.metric("Current AQI", f"{packet['AQI']:.0f}", 
                               delta="Hazardous" if packet['Alert']=="YES" else "Normal",
                               delta_color="inverse")
                
                # New AI KPI
                pred_aqi = packet['Predicted_AQI']
                if pred_aqi > packet['AQI'] + 10:
                    trend = "↗️ Rising Fast"
                    trend_color = "off"
                elif pred_aqi < packet['AQI'] - 10:
                    trend = "↘️ Improving"
                    trend_color = "normal"
                else:
                    trend = "➡️ Stable"
                    trend_color = "off"
                    
                kpi_latency.metric("AI Forecast (1hr)", f"{pred_aqi:.0f} AQI", trend, delta_color=trend_color)
                
                # AI Early Warning Status
                if pred_aqi > 100 and packet['AQI'] < 100:
                    kpi_status.warning(f"⚠️ EARLY WARNING: Hazardous Air Predicted in 45m!")
                else:
                    status_icon = "🟢" if packet['Alert'] == "NO" else "🔴"
                    kpi_status.info(f"{status_icon} System Status: {packet['Category']}")
                
                # Charts (Native Line Chart avoids full redraw flicker)
                # We transform the buffer to a dataframe just for the chart
                df_live = pd.DataFrame(live_buffer)
                
                with chart_container:
                     st.line_chart(df_live[['AQI', 'Predicted_AQI']], height=250)

                
                # Logs
                with log_container:
                    st.dataframe(
                        df_live[['timestamp', 'AQI', 'Edge_Latency', 'Category']].iloc[::-1],
                        height=200, 
                        hide_index=True,
                        column_config={"timestamp": "Time", "Edge_Latency": "Latency (ms)"}
                    )
                
                # Alerts
                with alert_container:
                    alerts = [p for p in live_buffer if p['Alert'] == "YES"]
                    if alerts:
                        for a in alerts[-3:]: # Show last 3
                            st.error(f"⚠️ AQI {a['AQI']:.0f} detected at {a['timestamp']}")
                    else:
                        st.success("No active alerts.")

                time.sleep(sim_speed)
                
        except StopIteration:
            st.warning("Simulation finished (End of Data).")
            st.session_state.is_running = False

# === TAB 2: HISTORICAL ANALYSIS ===
with tab_history:
    st.header("📊 Post-Incident Analysis")
    
    # Load data from DB
    df_hist = database.get_readings(limit=1000)
    
    if not df_hist.empty:
        col_h1, col_h2 = st.columns([3, 1])
        
        with col_h1:
            st.subheader("AQI Trends")
            st.line_chart(df_hist.set_index('id')['aqi'])
            
        with col_h2:
            st.subheader("Statistics")
            avg_aqi = df_hist['aqi'].mean()
            max_aqi = df_hist['aqi'].max()
            total_alerts = df_hist['alert_triggered'].sum()
            
            st.metric("Average AQI", f"{avg_aqi:.1f}")
            st.metric("Peak AQI", f"{max_aqi:.0f}")
            st.metric("Total Alerts", int(total_alerts))
            
        st.divider()
        st.subheader("Latency Comparison (Edge vs Cloud)")
        
        # Melt for comparison chart
        df_lat = df_hist[['id', 'edge_latency', 'cloud_latency']].melt('id', var_name='Type', value_name='Latency')
        
        # Altair chart for better aesthetics
        c = alt.Chart(df_lat).mark_line().encode(
            x='id',
            y='Latency',
            color='Type',
            tooltip=['Latency', 'Type']
        ).interactive()
        st.altair_chart(c, use_container_width=True)
        
        # Export
        csv = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Full Report (CSV)",
            csv,
            "air_quality_report.csv",
            "text/csv"
        )
    else:
        st.info("No historical data found. Run the simulation to generate data.")

# === TAB 3: SYSTEM HEALTH ===
with tab_system:
    st.header("System Diagnostics")
    c1, c2 = st.columns(2)
    with c1:
        st.success("Edge Node: ONLINE")
        st.info("Computing Unit: ARM Cortex-M4 (Simulated)")
        st.progress(35, text="CPU Usage: 35%")
    with c2:
        st.warning("Cloud Gateway: HIGH LATENCY")
        st.info("Region: aws-us-east-1")
        st.progress(92, text="Link Saturation: 92%")

