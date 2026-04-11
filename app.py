from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pickle
import numpy as np
from twilio.rest import Client

app = Flask(__name__)
# NEW: Secret key is required to secure user login sessions
app.secret_key = "super_secret_farm_key" 

# ==========================================
# TWILIO SETUP 
# ==========================================
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_SID_HERE"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_TOKEN_HERE"
TWILIO_PHONE_NUMBER = '+16624384476' 
YOUR_PERSONAL_NUMBER = '+18777804236' 

try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    print(f"Twilio init error: {e}")
# ==========================================

# Load the trained model
print(" * Loading AI Model...")
with open('soil_model.pkl', 'rb') as f:
    model = pickle.load(f)
print(" * Model loaded successfully!")

latest_sensor_data = {
    "N": 0, "P": 0, "K": 0, 
    "temperature": 0.0, "humidity": 0.0, "ph": 0.0, "rainfall": 0.0, 
    "predicted_crop": "Waiting for sensor data...",
    "advisory": "Waiting for sensor data..."
}

# ==========================================
# NEW: LOGIN & AUTHENTICATION ROUTES
# ==========================================
@app.route('/')
def home():
    # If they are already logged in, send them straight to the dashboard
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    # Otherwise, show the login page
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Hardcoded credentials for project demo
    if username == 'farmer' and password == 'farm123':
        session['logged_in'] = True  # Save login state in session
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid credentials. Please try again.")

@app.route('/logout')
def logout():
    session.pop('logged_in', None) # Remove login state
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    # SECURITY: If someone tries to access /dashboard without logging in, kick them out!
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    return render_template('index.html')
# ==========================================

@app.route('/api/live-data', methods=['GET'])
def get_live_data():
    return jsonify(latest_sensor_data)

@app.route('/predict', methods=['POST'])
def predict():
    global latest_sensor_data
    try:
        data = request.json
        features = [
            data['N'], data['P'], data['K'], 
            data['temperature'], data['humidity'], 
            data['ph'], data['rainfall']
        ]
        
        prediction = model.predict([features])[0]
        
        advisory = "Standard NPK application recommended."
        if prediction == "Rice":
            advisory = "Ensure field is flooded to 5cm."
        elif prediction == "Maize":
            advisory = "Ensure good drainage. Apply Zinc if needed."

        # SMS Alert Logic
        if data['N'] < 60 or data['temperature'] > 35.0:
            alert_message = f"⚠️ FARM ALERT: Critical levels detected!\nCrop: {prediction}\nNitrogen: {data['N']}\nTemp: {data['temperature']}°C"
            try:
                twilio_client.messages.create(body=alert_message, from_=TWILIO_PHONE_NUMBER, to=YOUR_PERSONAL_NUMBER)
            except Exception:
                pass

        response = {
            'predicted_crop': prediction,
            'advisory': advisory,
            'status': 'success'
        }
        
        print(f"Received: {features} -> Prediction: {prediction}")
        
        latest_sensor_data = data.copy()
        latest_sensor_data['predicted_crop'] = str(prediction)
        latest_sensor_data['advisory'] = advisory
        
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)