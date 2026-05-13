<div align="center">
  <img width="1436" height="778" alt="Screenshot 2026-05-13 at 12 04 13 PM" src="https://github.com/user-attachments/assets/67fef30d-4678-4510-b8a5-e9bf23b2cf6e" />
<img width="1421" height="781" alt="Screenshot 2026-05-13 at 12 03 36 PM" src="https://github.com/user-attachments/assets/e2a2cdd8-74a2-431e-9983-5d96c7f73164" />
  <h1>🌱 IoT-Enabled Precision Agriculture & AI Soil Monitoring</h1>
  <p>A full-stack IoT and Machine Learning solution for modern farming, providing real-time crop recommendations and critical soil health alerts via a secure web dashboard and SMS notifications.</p>
</div>

<div align="center">

[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)](https://github.com/SahilSinhaDev-cpu/-IoT-Enabled-Precision-Agriculture-System-with-AI-Driven-Soil-Health-Monitoring)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=for-the-badge&logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Twilio](https://img.shields.io/badge/Twilio-SMS_API-red?style=for-the-badge&logo=twilio)](https://www.twilio.com)

</div>

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🧠 AI Crop Recommendation** | A **Random Forest Classifier**, trained on a 3,500-sample dataset, predicts the optimal crop (e.g., Rice, Maize, Coffee) based on live soil and environmental data. |
| **📡 Real-Time IoT Processing** | A decoupled architecture where edge sensors (simulated or physical) transmit JSON data to a central Flask REST API for processing. |
| **📊 Dynamic Web Dashboard** | A secure, login-protected dashboard built with Flask and vanilla JavaScript. It uses AJAX polling to display live data, charts, and AI insights without page reloads. |
| **🚨 Automated SMS Alerts** | Integrates with the **Twilio API** to send instant SMS notifications to the farmer's phone when critical thresholds (e.g., low nitrogen, high temperature) are breached. |
| **🔒 Secure User Authentication** | The dashboard is protected by a session-based login system, ensuring that only authorized users can view sensitive farm data. |
| **🌓 Light & Dark Mode** | A modern, user-friendly interface with a persistent light/dark mode toggle for comfortable viewing in any environment. |

## 🏗️ System Architecture
The project follows a classic 4-tier IoT architecture, ensuring modularity and scalability from the edge to the cloud.

```mermaid
graph TD
    subgraph Perception Layer [Edge Devices & Sensors]
        S[IoT Simulator / ESP32] -->|JSON Payload via HTTP| N
    end

    subgraph Network Layer [Communication]
        N[REST API Endpoint] --> F
    end

    subgraph Processing Layer [Server & AI Brain]
        F[Flask API Server - app.py]
        M[(Random Forest ML Model - soil_model.pkl)]
        F -->|Analyzes Data & Queries Model| M
    end

    subgraph Application Layer [Interfaces & Actions]
        D[Real-Time Web Dashboard - index.html]
        T[Twilio Cloud API]
        F -->|Serves Data to Frontend| D
        F -->|Triggers SMS on Critical Events| T
    end

    subgraph End User
        U[Farmer]
        D -->|Visual Display| U
        T -->|SMS Warning Alert| U
    end

    %% Styling
    style S fill:#e6f2ff,stroke:#0055cc
    style F fill:#d4edda,stroke:#155724
    style M fill:#fff3cd,stroke:#856404
    style D fill:#f8d7da,stroke:#721c24
    style T fill:#fca,stroke:#e65100
```

---

## 🛠️ Technology Stack & Codebase

This project utilizes a modern stack for web development, machine learning, and cloud communication.

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | ![Python](https://img.shields.io/badge/-Python-blue?logo=python) ![Flask](https://img.shields.io/badge/-Flask-black?logo=flask) | Core application logic, REST API, and serving the web interface. |
| **Frontend** | ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?logo=html5) ![CSS3](https://img.shields.io/badge/-CSS3-1572B6?logo=css3) ![JavaScript](https://img.shields.io/badge/-JavaScript-yellow?logo=javascript) | Building the dynamic, responsive, and interactive user dashboard. |
| **Machine Learning** | ![Scikit-Learn](https://img.shields.io/badge/-Scikit--Learn-orange?logo=scikit-learn) ![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas) | Training the Random Forest model and handling the agricultural dataset. |
| **Cloud Services** | ![Twilio](https://img.shields.io/badge/-Twilio-F22F46?logo=twilio) | Sending programmatic SMS alerts for critical soil conditions. |
| **Data Visualization** | ![Chart.js](https://img.shields.io/badge/-Chart.js-FF6384?logo=chart.js) | Rendering live, animated line charts for nutrient levels on the dashboard. |

### Codebase Structure

```
├── .gitignore             # Specifies files for Git to ignore (e.g., .env, *.pkl).
├── app.py                 # Main Flask application: handles routing, API endpoints, and business logic.
├── simulator.py           # Simulates an IoT device sending sensor data to the Flask server.
├── train_model.py         # Script to generate synthetic data and train the Random Forest model.
├── soil_model.pkl         # The pre-trained, serialized machine learning model file.
├── requirements.txt       # A list of all Python dependencies for the project.
├── .env                   # (You create this) Stores secret keys and API credentials.
└── templates/
    ├── base.html          # Base HTML template with Bootstrap and FontAwesome.
    ├── index.html         # The main dashboard page with all the data visualization components.
    └── login.html         # The secure login page for user authentication.
```

---

## 🚀 Getting Started

Follow these instructions to get a local copy of the project up and running.

### 1. Prerequisites
*   Python 3.8+
*   A Twilio account with an active phone number (for SMS alerts)

### 2. Installation & Setup

**A. Clone the repository:**
```bash
git clone https://github.com/SahilSinhaDev-cpu/-IoT-Enabled-Precision-Agriculture-System-with-AI-Driven-Soil-Health-Monitoring.git
cd -IoT-Enabled-Precision-Agriculture-System-with-AI-Driven-Soil-Health-Monitoring
```

**B. Create a virtual environment and install dependencies:**
```bash
# Create a virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate
# On Windows, use: venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
```

**C. Set up environment variables:**
Create a file named `.env` in the root of the project directory. This file will securely store your API keys. Copy the contents of `.env.example` (if provided) or use the template below.

```ini
# .env
SECRET_KEY="a_very_strong_random_secret_key_for_flask_sessions"
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_twilio_auth_token"
TWILIO_PHONE_NUMBER="+15017122661"
YOUR_PERSONAL_NUMBER="+15558675309" # The number to receive SMS alerts
```

### 3. Running the System

The system runs in two parts: the server and the simulator. You will need two separate terminal windows.

**Terminal 1: Start the Flask Web Server**
```bash
python app.py
```
The server will start on `http://127.0.0.1:5001`.

**Terminal 2: Start the IoT Simulator**
```bash
python simulator.py
```
The simulator will begin sending data to the server every 3 seconds.

### 4. Access the Dashboard
Open your web browser and navigate to **`http://127.0.0.1:5001`**.
Log in with the demo credentials:
*   **Username:** `farmer`
*   **Password:** `farm123`

You should now see the live dashboard, with data updating in real-time!

---

## 🔮 Future Enhancements

*   **Hardware Integration:** Replace `simulator.py` with a Python script running on an ESP32 or Raspberry Pi connected to physical NPK, DHT11, and pH sensors.
*   **Database Logging:** Integrate a database like SQLite or PostgreSQL to log historical sensor data for trend analysis and long-term performance tracking.
*   **Advanced Advisories:** Enhance the AI to provide more detailed advisories, such as specific fertilizer quantities or pest control recommendations.
