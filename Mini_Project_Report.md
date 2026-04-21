# EdgeSafe Monitor: Edge-Based Air Quality Early Warning System


---

## TABLE OF CONTENTS

| S.No. | Contents | Page no. |
| :---: | :--- | :--- |
| 1. | Abstract | [Page no] |
| 2. | Introduction | [Page no] |
| 3. | Literature survey | [Page no] |
| 4. | Problem Statement and Objectives | [Page no] |
| 5. | Hardware and Software requirements | [Page no] |
| 6. | Implementation | [Page no] |
| 7. | Results & Discussion | [Page no] |
| 8. | Conclusion & Future Scope | [Page no] |
| 9. | References | [Page no] |

---

## 1. ABSTRACT

This project presents "EdgeSafe Monitor," a decentralized, edge-based air quality early warning system designed to overcome the latency and connectivity issues inherent in traditional cloud-centric monitoring solutions. By deploying a lightweight AI inference engine directly on edge devices, the system processes sensor readings and predicts Air Quality Index (AQI) locally. This approach drastically reduces the response time for safety alerts from several seconds (in cloud systems) to approximately 50 milliseconds. The system autonomously activates critical warnings during hazardous pollutant spikes (such as CO or NO2) without relying on a consistent internet connection, ensuring continuous, reliable, and real-time safety monitoring in both urban and remote environments.

---

## 2. INTRODUCTION

Rapid urbanization and industrialization have led to deteriorating air quality, posing severe health risks to city dwellers globally. Traditional monitoring systems heavily rely on cloud computing, where raw sensor data is continuously transmitted to centralized servers for processing and analysis. While effective for historical logging, this architecture introduces significant network latency—often delaying critical responses by 2 to 5 seconds. In emergency situations, such as sudden gas leaks or severe pollutant spikes, this delay can be life-threatening. Furthermore, these systems are highly vulnerable to internet outages, rendering them useless in disconnected or remote environments.

To address these limitations, the "EdgeSafe Monitor" project shifts the computational intelligence from the cloud directly to the local edge node. By running a localized Machine Learning inference engine, the system analyzes data instantly on the device, ensuring ultra-low latency and unparalleled reliability for life-safety critical alerts. Cloud connectivity is reserved solely for non-urgent tasks like long-term historical analysis.

---

## 3. LITERATURE SURVEY

1. **Cloud-Based Air Quality Monitoring Systems:** Previous studies have extensively explored cloud-centric IoT networks for monitoring CO and NO2 levels. While these systems excel at big data analytics and long-term trend forecasting, they consistently exhibit high latency during real-time alert generation due to the round-trip time required for data transmission.
2. **Edge Computing in IoT:** Recent research has demonstrated the efficacy of edge computing in reducing bandwidth and latency. Various projects have deployed lightweight algorithms on microcontrollers to pre-process data before cloud transmission, though many still rely on the cloud for final decision-making.
3. **Machine Learning on Edge Devices (TinyML):** Existing literature highlights the growing trend of deploying compressed ML models (like Random Forests or lightweight Neural Networks) directly onto resource-constrained devices, enabling offline inference and autonomous operation.
4. **Smart City Environmental Sensing:** Several smart city initiatives have deployed distributed sensor frameworks. However, a common gap identified in the literature is the lack of immediate, localized feedback mechanisms that function independently of central municipal servers during network failures.
5. **Real-time Gas Leak Detection:** Prior works on industrial gas detection systems emphasize the critical need for sub-second response times. These projects often utilize dedicated, hardwired alarm systems, lacking the predictive AI capabilities and data-logging features provided by modern edge-IoT hybrid architectures.

---

## 4. Problem Statement and Objectives

**Problem Statement:**  
Traditional cloud-based air quality monitoring systems suffer from high latency and complete failure during network outages, preventing immediate warnings during critical pollutant spikes.

**Problem Description:**  
Centralized architectures require raw sensor data to be transmitted to remote servers for processing, which introduces varying network delays (typically 2-5 seconds). In critical safety scenarios, this delay is unacceptable and the dependency on internet connectivity creates a single point of failure that compromises continuous monitoring.

**Objectives:**  
1. Develop a decentralized edge computing system to shift AI inference from the cloud to the local device.
2. Achieve real-time processing with a response time of ~50ms for air quality predictions and alerts.
3. Ensure the system can operate autonomously and trigger safety alerts without requiring active internet connectivity.
4. Develop a dashboard for real-time visualization of sensor streams, alerts, and system health.

---

## 5. HARDWARE AND SOFTWARE REQUIREMENTS

**Hardware Requirements:**
* Edge Computing Unit: Raspberry Pi 4 Model B (4GB RAM) or NVIDIA Jetson Nano.
* Microcontroller (Low Power): ESP32 or STM32 (ARM Cortex-M4) for raw sensor interfacing.
* Sensors:
  * CO Sensor: MQ-7 (Carbon Monoxide)
  * NO2/O3 Sensor: MiCS-6814 (Nitrogen Dioxide / Ozone)
  * Environmental: DHT22 (Temperature & Humidity)
* Connectivity: Wi-Fi Module (ESP8266/Integrated), LoRaWAN Module (SX1276) [Optional].
* Power Supply: 5V 3A USB-C Power Adapter or Li-Po Battery Pack.

**Software Requirements:**
* Operating System: Windows 10/11 (for Simulation) or Raspberry Pi OS (Linux).
* Programming Language: Python 3.9+.
* Core Libraries: `pandas`, `numpy`, `scikit-learn`, `joblib`, `streamlit`, `altair`, `plotly`.
* Development Tools: VS Code, Git.

---

## 6. IMPLEMENTATION
1. **Frontend:** Streamlit (`streamlit`) for the interactive "Digital Twin" dashboard.
2. **Backend:** Python (`pandas`, `scikit-learn`) for the local AI Inference Engine.
3. **API Integration:** Pre-trained ML models (`joblib`) and simulated sensor streams.

1. **Frontend (Python/Streamlit):**
* `main.py` / `dashboard.py`: Contains the Streamlit visual setup, layout configurations, real-time charting using Altair/Plotly, and status indicators.
2. **Backend (Python):**
* `src/data_processing.py`: Handles local data cleaning and noise reduction.
* `src/inference.py`: Loads the trained lightweight model (`edge_forecast_model.pkl`) and performs local prediction on incoming data blocks.
* `train_model.py`: Script used offline to train the machine learning models.
3. **API Integration:**
* Local integration involves piping simulated IoT sensor data streams directly into the backend Python processing functions without intermediate network calls, ensuring sub-100ms processing times.

---

## 7. RESULTS & DISCUSSION

*[Insert Output Website Screen Shots Here]*
**Figure 1:** Real-time Dashboard displaying current CO, NO2, and predicted AQI levels.
**Figure 2:** System Alert Interface showing an immediate local warning triggered by an anomalous pollutant spike.

**Discussion:**
The simulation confirms that the Edge approach successfully addresses the problem statement. The edge-based local inference setup achieved a response time of ~50 milliseconds. When compared to the estimated Cloud approach's ~2000 milliseconds, this represents an approximate 97% improvement in alert speed, proving the system's effectiveness for life-safety critical monitoring.

---

## 8. CONCLUSION & FUTURE SCOPE

**Conclusion:**
The project successfully developed and simulated the "EdgeSafe Monitor," demonstrating that transitioning computational intelligence from a centralized cloud to an edge device drastically reduces system latency. The objectives were met by achieving a ~50ms response time and providing autonomous, offline capability for predicting AQI and triggering critical alerts. 

**Future Scope:**
* **Near-term:** Integrate physical hardware sensors (ESP32, MQ-7) to replace the simulation engine and conduct field testing in real-world urban environments.
* **Medium-term:** Implement LoRaWAN connectivity to allow edge nodes to communicate across long distances with minimal power, ensuring data delivery even when local Wi-Fi fails.
* **Long-term:** Implement Federated Learning, enabling multiple edge nodes to collaboratively train and improve the AI model without sharing raw data, enhancing privacy and overall system accuracy across a wider geographic area.

---

## 9. REFERENCES

1. [URL linking to Cloud-based Air Quality System Example 1]
2. [URL linking to Edge IoT Implementation Example 2]
3. [URL linking to TinyML on ESP32 Project Example 3]
4. [URL linking to Smart City Environmental Sensing Example 4]
5. [URL linking to Gas Leak Detection Alert System Example 5]

