# Edge-Based Air Quality Early Warning System
## Project Documentation & Report Structure

### 1. Title & Abstract
**Title:** Simulation of an Edge-Based Air Quality Early Warning System using Real-Time Sensor Processing.

**Abstract:**
Urban air pollution poses severe health risks that demand immediate mitigation. Traditional cloud-based monitoring systems suffer from high latency, delaying critical alerts. This project implements a simulated Edge Computing architecture that processes simulated sensor data (CO, NO2, O3) locally to trigger instant health warnings (AQI > 100). The simulation demonstrates that edge-based decision-making achieves millisecond-level response times (~50ms) compared to cloud-based delays (~2000ms), significantly enhancing urban safety and aligning with SDG 3 and SDG 11.

---

### 2. Introduction
- **Problem:** Centralized cloud systems are too slow for real-time safety alerts.
- **Solution:** Move decision logic to the "Edge" (local device).
- **Goal:** Quantify the latency difference between Edge and Cloud architectures.

### 3. Methodology
#### 3.1 Data Source
- **Dataset:** UCI Air Quality Dataset (Time-series).
- **Simulation:** Data is streamed row-by-row to mimic live sensor inputs.

#### 3.2 System Architecture
- **Edge Node:** Implements lightweight AQI calculation and threshold logic. No dependencies.
- **Cloud Node:** Simulates network transmission (RTT), queuing, and database storage lag.

### 4. Implementation Details
- **Tech Stack:** Python, Pandas, Streamlit.
- **Algorithm:** Deterministic EPA AQI formula (Piecewise linear interpolation).

### 5. Results (Simulation)
| Metric | Edge Node | Cloud Node |
|:---|:---:|:---:|
| **Processing Loc** | Local (Device) | Remote Server |
| **Network Delay** | 0 ms | ~2000ms (Internet) |
| **Avg Response** | **~50 ms** | **~2500 ms** |
| **Alert Speed** | Immediate | Delayed |

### 6. Conclusion
The simulation proves that edge computing reduces response latency by over **97%** compared to cloud processing. For hazardous gas detection, this speed difference saves lives.

### 7. Future Work
- Deploy on Raspberry Pi / ESP32.
- Integrate LoRaWAN for city-wide coverage.
