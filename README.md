# 🌱 IoT-Enabled Precision Agriculture System with AI-Driven Soil Health Monitoring

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-black)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-Random_Forest-orange)

## 📌 Project Overview
This project is a full-stack IoT and Machine Learning solution designed to modernize farming practices. It actively monitors environmental and soil metrics (Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, and Rainfall) and uses a pre-trained **Random Forest Classifier** to provide real-time crop recommendations. 

Additionally, it features a secure web dashboard for real-time visualization and integrates with the **Twilio API** to send critical SMS alerts directly to the farmer's mobile device when soil conditions degrade.

*(Note to Self: Add a screenshot of your beautiful green dashboard here later!)*

---

## ✨ Key Features
* **🧠 AI-Powered Crop Recommendation:** Scikit-Learn ML model trained on a 3000+ row agricultural dataset to predict the optimal crop based on real-time soil chemistry.
* **📡 Real-Time IoT Data Processing:** A decoupled architecture where edge sensors (currently simulated, hardware-ready for ESP32) transmit JSON payloads to a REST API.
* **📊 Dynamic Web Dashboard:** A secure, AJAX-driven Flask frontend that updates live sensor readings without requiring page reloads.
* **🚨 Automated SMS Alerts:** Cloud integration via Twilio to notify users instantly if critical thresholds (e.g., extreme temperatures or nutrient deficiencies) are breached.
* **🔒 Secure Authentication:** Route protection ensuring only authorized users can access the farm's live dashboard.

---
🛠️ Technology Stack
Backend: Python, Flask, RESTful APIs

Machine Learning: Scikit-Learn, Pandas, NumPy

Frontend: HTML5, CSS3, Vanilla JavaScript (AJAX/Fetch)

Cloud & Services: Twilio API (SMS)

Version Control: Git & GitHub

---

🚀 Installation & Setup
1. Clone the Repository
git clone [https://github.com/SahilSinhaDev-cpu/-IoT-Enabled-Precision-Agriculture-System-with-AI-Driven-Soil-Health-Monitoring.git](https://github.com/SahilSinhaDev-cpu/-IoT-Enabled-Precision-Agriculture-System-with-AI-Driven-Soil-Health-Monitoring.git)
cd -IoT-Enabled-Precision-Agriculture-System-with-AI-Driven-Soil-Health-Monitoring

2. Install Dependencies
Ensure you have Python installed, then install the required packages:
pip install -r requirements.txt

3. Environment Variables (Twilio Setup)
To enable SMS alerts safely, create a .env file in the root directory and add your Twilio credentials:
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
FARMER_PHONE_NUMBER=+0987654321

5. Run the System
You need two terminal windows to run the full decoupled system.

Terminal 1 (Start the Server):
python app.py
Terminal 2 (Start the Edge Simulator):
python simulator.py
Open your browser and navigate to http://127.0.0.1:5001 to access the dashboard.
🔮 Future Enhancements
Phase 2 (Hardware Integration): Replace simulator.py with an ESP32 microcontroller wired to physical NPK, DHT11 (Temp/Humidity), and soil moisture sensors.

Data Logging: Integrate an SQLite or PostgreSQL database to track historical farm data and visualize long-term trends.

---

## 🏗️ System Architecture
The system is built on a highly modular 4-tier IoT architecture:

```mermaid
graph TD
    subgraph Perception Layer [Edge Devices & Sensors]
        S[Simulator.py / Future ESP32] -->|Generates: NPK, Temp, pH, Rain| N
    end

    subgraph Network Layer [Communication]
        N((HTTP POST JSON Payload)) --> F
    end

    subgraph Processing Layer [Server & AI Brain]
        F[Flask API Server - app.py]
        M[(Random Forest ML Model - soil_model.pkl)]
        F <-->|Requests & Receives Crop Prediction| M
    end

    subgraph Application Layer [Interfaces & Actions]
        D[Real-Time Web Dashboard - index.html]
        T[Twilio Cloud API]
        F -->|Serves Data via HTTP GET| D
        F -->|Triggers on Critical Thresholds| T
    end

    subgraph End User
        U((The Farmer / Evaluator))
        D -->|Visual Display| U
        T -->|SMS Warning Alert| U
    end

    %% Styling to make it look professional
    style S fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#dfd,stroke:#333,stroke-width:2px
    style D fill:#fdd,stroke:#333,stroke-width:2px
    style T fill:#fca,stroke:#333,stroke-width:2px

