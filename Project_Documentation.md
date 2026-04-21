# EdgeSafe Monitor: Edge-Based Air Quality Early Warning System

## 1. Problem Statement
Rapid urbanization has led to deteriorating air quality, posing severe health risks to city dwellers. Traditional air quality monitoring systems rely on centralized cloud architectures where sensor data is transmitted to remote servers for processing. This approach introduces significant **latency (network delays)**, typically ranging from 2 to 5 seconds or more, and creates a single point of failure. In critical scenarios—such as a sudden gas leak or spike in hazardous pollutants (CO, NO2)—this delay prevents immediate warnings, potentially endangering lives. Furthermore, cloud-dependent systems fail completely when internet connectivity is unstable, which is common in remote or industrial edge environments.

## 2. Proposed Solution
We propose **"EdgeSafe Monitor,"** a decentralized edge computing system that shifts intelligence from the cloud to the local device. Instead of sending raw data to a server, the edge node (simulated as an ARM Cortex-M4/Raspberry Pi) collects sensor readings and runs a lightweight **AI Inference Engine** locally. This allows the system to calculate the Air Quality Index (AQI) and predict hazardous trends in **real-time (~50ms)**. The system autonomously triggers immediate alerts when safety thresholds are breached, ensuring 24/7 safety regardless of internet connectivity. Cloud connectivity is used only for asynchronous logging and long-term historical analysis, optimizing bandwidth and responsiveness.

## 3. Hardware Requirements
To implement the EdgeSafe Monitor in a real-world deployment, the following hardware is required (simulated in this project):

*   **Edge Computing Unit:** Raspberry Pi 4 Model B (4GB RAM) or NVIDIA Jetson Nano.
*   **Microcontroller (Low Power):** ESP32 or STM32 (ARM Cortex-M4) for raw sensor interfacing.
*   **Sensors:**
    *   **CO Sensor:** MQ-7 (Carbon Monoxide)
    *   **NO2/O3 Sensor:** MiCS-6814 (Nitrogen Dioxide / Ozone)
    *   **Environmental:** DHT22 (Temperature & Humidity)
*   **Connectivity:**
    *   Wi-Fi Module (ESP8266/Integrated)
    *   LoRaWAN Module (SX1276) for long-range, low-power transmission (optional).
*   **Power Supply:** 5V 3A USB-C Power Adapter or Li-Po Battery Pack.

## 4. Software Requirements
The project is built using a Python-based technology stack optimized for modular simulation and edge deployment:

*   **Operating System:** Windows 10/11 (for Simulation) or Raspberry Pi OS (Linux).
*   **Programming Language:** Python 3.9+.
*   **Core Libraries:**
    *   **`pandas` / `numpy`:** For efficient time-series data alignment and processing.
    *   **`scikit-learn`:** For training and running the lightweight Random Forest Regressor model locally.
    *   **`joblib`:** For efficient model serialization (loading the trained AI model).
    *   **`streamlit`:** For the interactive "Digital Twin" dashboard and real-time visualization.
    *   **`altair` / `plotly`:** For high-performance interactive data charting.
*   **Development Tools:** VS Code, Git.

## 5. System Architecture & Methodology
The system follows a three-layer architecture:
1.  **Perception Layer:** Simulated sensors generate continuous streams of pollutant data (CO, NO2, O3).
2.  **Edge Processing Layer:**
    *   **Data Cleaning:** Handling missing values and noise locally.
    *   **Inference:** A pre-trained Machine Learning model (`models/edge_forecast_model.pkl`) predicts the next-hour AQI.
    *   **Decision Logic:** If AQI > 100, a local alert is triggered immediately (`Alert=YES`).
3.  **Application Layer:** A Dashboard visualizes the real-time stream, alerts, and system health status. 

**Performance Result:** The simulation confirms that the Edge approach achieves a response time of **~50 milliseconds**, compared to the Cloud approach's **~2000 milliseconds**, representing a **97% improvement** in alert speed.
