from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response, g
import pickle
import numpy as np
from twilio.rest import Client
import os
from dotenv import load_dotenv
import openai
import logging
import click
import io
import csv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- 1. INITIALIZATION AND CONFIGURATION ---

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()  # Load environment variables from .env file

# --- API & Secret Key Configuration ---
logging.info("Loading environment variables and API keys...")
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
YOUR_PERSONAL_NUMBER = os.getenv('YOUR_PERSONAL_NUMBER')

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a_very_strong_random_secret_key")

DATABASE_FILE = 'agri_data.db'
# --- Global Variables & Constants ---

# Initialize Twilio client once
try:
    if account_sid and auth_token:
        twilio_client = Client(account_sid, auth_token)
        logging.info("Twilio client initialized successfully.")
    else:
        twilio_client = None
        logging.warning("Twilio credentials not found. SMS alerts will be disabled.")
except Exception as e:
    twilio_client = None
    logging.error(f"Failed to initialize Twilio client: {e}")

# Load the trained model once at startup
try:
    logging.info("Loading AI Model...")
    with open('soil_model.pkl', 'rb') as f:
        model = pickle.load(f)
    logging.info("Model loaded successfully!")
except FileNotFoundError:
    logging.critical("Fatal Error: soil_model.pkl not found. The application cannot run without the model.")
    exit() # Exit if the core model is missing

# In-memory data store for the latest sensor readings.
# NOTE: In a multi-worker production environment (like Gunicorn), this would not be shared
# across workers. A dedicated cache like Redis or Memcached would be a better solution.
latest_sensor_data = {
    "N": 0, "P": 0, "K": 0, 
    "temperature": 0.0, "humidity": 0.0, "ph": 0.0, "rainfall": 0.0, 
    "predicted_crop": "Waiting for sensor data...",
    "advisory": "Waiting for sensor data...",
    "status": "OPTIMAL" # NEW: Add status to the global state
}

# Centralized dictionary for crop advisories for easier management
CROP_ADVISORIES = {
    "Rice": "Ensure field is flooded to 5cm.",
    "Maize": "Ensure good drainage. Apply Zinc if needed.",
    "Soybean": "Ensure proper soil inoculation for nitrogen fixation. Monitor for common pests.",
    "Default": "Standard NPK application recommended."
}

MAX_CHAT_PAYLOAD_SIZE = 4096 # 4KB limit for chat messages

# --- Database Connection Handling ---
def get_db():
    """
    Opens a new database connection if there is none yet for the current application context.
    The connection is stored in Flask's 'g' object, which is unique for each request.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_FILE)
        g.db.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Database Initialization Command ---
@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables and a default admin user."""
    db = get_db()
    
    # Create tables
    db.execute('''
        CREATE TABLE IF NOT EXISTS sensor_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            N INTEGER, P INTEGER, K INTEGER,
            temperature REAL, humidity REAL, ph REAL, rainfall REAL,
            predicted_crop TEXT
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    click.echo('Created database tables.')

    # Create default user
    default_username = 'farmer'
    cursor = db.execute("SELECT id FROM users WHERE username = ?", (default_username,))
    if cursor.fetchone() is None:
        password_hash = generate_password_hash('farm123')
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (default_username, password_hash))
        click.echo(f"Created default user '{default_username}'.")
    
    db.commit() # Commit all changes
    click.echo('Initialized the database.')

# --- 2. AUTHENTICATION & CORE WEB ROUTES ---

@app.route('/')
def home():
    """Renders the login page or redirects to the dashboard if already logged in."""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handles user login.

    Authenticates against the users table in the database. On success,
    sets a session variable and redirects to the dashboard. On failure,
    re-renders the login page with an error message.
    """
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('login.html', error="Username and password are required.")

    try:
        db = get_db()
        user_record = db.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()

        if user_record and check_password_hash(user_record[0], password):
            session['logged_in'] = True
            logging.info(f"User '{username}' logged in successfully.")
            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"Failed login attempt for username: '{username}'.")
            return render_template('login.html', error="Invalid credentials. Please try again.")

    except sqlite3.Error as e:
        logging.error(f"Database error during login: {e}", exc_info=True)
        return render_template('login.html', error="A database error occurred. Please try again later.")

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """Renders the main dashboard page.
    
    This route is protected; it redirects to the login page if the user
    is not authenticated.
    """
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/history')
def history():
    """Renders the historical data visualization page."""
    if 'logged_in' not in session:
        logging.warning("Unauthorized attempt to access /history.")
        return redirect(url_for('home'))
    logging.info("Rendering history page.")
    return render_template('history.html')

# --- 3. API ENDPOINTS ---

@app.route('/api/live-data', methods=['GET'])
def get_live_data():
    """Provides the latest sensor data to the frontend for polling."""
    return jsonify(latest_sensor_data)

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Retrieves sensor data records from the database.
    Accepts 'start' and 'end' query parameters for date range filtering.
    Defaults to the last 100 records if no date range is provided.
    """
    if 'logged_in' not in session:
        logging.warning("Unauthorized attempt to access /api/history.")
        return jsonify({'error': 'Unauthorized'}), 401

    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')

    try:
        db = get_db()
        query = "SELECT * FROM sensor_history"
        params = []

        if start_date_str and end_date_str:
            # Add time component to make the range inclusive
            start_datetime = f"{start_date_str} 00:00:00"
            end_datetime = f"{end_date_str} 23:59:59"
            query += " WHERE timestamp BETWEEN ? AND ?"
            params.extend([start_datetime, end_datetime])
            logging.info(f"Fetching history for date range: {start_datetime} to {end_datetime}")
        
        query += " ORDER BY timestamp DESC"

        if not (start_date_str and end_date_str):
            query += " LIMIT 100"
            logging.info("Fetching last 100 history records (no date range).")

        rows = db.execute(query, params).fetchall()
        # Convert the list of sqlite3.Row objects into a standard list of dictionaries
        history_data = [dict(row) for row in rows]

        logging.info(f"Successfully retrieved {len(history_data)} records from history.")
        return jsonify(history_data)

    except sqlite3.Error as e:
        logging.error(f"Database error in /api/history: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve historical data from the database.'}), 500

@app.route('/api/history/export', methods=['GET'])
def export_history():
    """
    Exports sensor data records to a CSV file.
    Accepts 'start' and 'end' query parameters for date range filtering.
    Defaults to the last 100 records if no date range is provided.
    """
    if 'logged_in' not in session:
        logging.warning("Unauthorized attempt to access /api/history/export.")
        return jsonify({'error': 'Unauthorized'}), 401

    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')

    try:
        db = get_db()
        query, params = "", []

        if start_date_str and end_date_str:
            start_datetime = f"{start_date_str} 00:00:00"
            end_datetime = f"{end_date_str} 23:59:59"
            query = "SELECT * FROM sensor_history WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC"
            params.extend([start_datetime, end_datetime])
            logging.info(f"Exporting history for date range: {start_datetime} to {end_datetime}")
        else:
            # Subquery to get the last 100 records but in chronological order for the export
            query = "SELECT * FROM (SELECT * FROM sensor_history ORDER BY timestamp DESC LIMIT 100) ORDER BY timestamp ASC"
            logging.info("Exporting last 100 history records (no date range).")

        rows = db.execute(query, params).fetchall()

        # Use an in-memory string buffer for the CSV
        output = io.StringIO()
        writer = csv.writer(output)

        if rows:
            writer.writerow(rows[0].keys())  # Write header
            writer.writerows(rows)           # Write data rows

        output.seek(0)

        return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=history_export.csv"})

    except sqlite3.Error as e:
        logging.error(f"Database error during CSV export: {e}", exc_info=True)
        return "Error generating CSV file.", 500

@app.route('/predict', methods=['POST'])
def predict():
    """
    Receives sensor data from the IoT simulator, runs the AI model prediction,
    updates the global state, and triggers alerts if necessary.
    """
    global latest_sensor_data

    # Validate incoming request
    if not request.json:
        logging.warning("Received request to /predict with no JSON payload.")
        return jsonify({'error': 'Invalid request. JSON payload required.'}), 400

    required_keys = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    if not all(key in request.json for key in required_keys):
        logging.warning(f"Received incomplete data for /predict. Missing keys.")
        return jsonify({'error': 'Missing one or more required sensor data keys.'}), 400

    try:
        data = request.json
        features = [
            data['N'], data['P'], data['K'], 
            data['temperature'], data['humidity'], 
            data['ph'], data['rainfall']
        ]
        
        prediction = model.predict([features])[0]
        
        # Log the incoming data and its prediction to the database
        log_to_db(data, prediction)
        
        # Get advisory from the centralized dictionary
        advisory = CROP_ADVISORIES.get(prediction, CROP_ADVISORIES["Default"])

        # Centralized Status Logic
        status = "OPTIMAL"
        is_critical = data['N'] < 60 or data['temperature'] > 35.0

        # Trigger SMS Alert if conditions are critical and Twilio is configured
        if is_critical and twilio_client:
            status = "CRITICAL"
            alert_message = f"⚠️ FARM ALERT: Critical levels detected!\nCrop: {prediction}\nNitrogen: {data['N']}\nTemp: {data['temperature']}°C"
            
            # Ensure phone numbers are configured before trying to send
            if TWILIO_PHONE_NUMBER and YOUR_PERSONAL_NUMBER:
                try:
                    message = twilio_client.messages.create(
                        body=alert_message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=YOUR_PERSONAL_NUMBER
                    )
                    logging.info(f"Twilio SMS sent successfully with SID: {message.sid}")
                except Exception as e:
                    logging.error(f"Twilio SMS failed to send: {e}")
            else:
                logging.warning("Critical event detected, but Twilio phone numbers are not configured. Skipping SMS.")

        # The response sent back to the simulator
        response = {
            'predicted_crop': prediction,
            'advisory': advisory,
            'status': 'success'
        }
        
        logging.info(f"Prediction successful: {features} -> {prediction}")
        
        # Update the global state for the dashboard to fetch
        latest_sensor_data = data.copy()
        latest_sensor_data['predicted_crop'] = str(prediction)
        latest_sensor_data['advisory'] = advisory
        latest_sensor_data['status'] = status
        
        return jsonify(response)

    except Exception as e:
        logging.error(f"An error occurred during prediction: {e}")
        return jsonify({'error': 'An internal server error occurred during prediction.'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat messages from the user, sends them to OpenAI, and returns the response."""
    if 'logged_in' not in session:
        logging.warning("Unauthorized chat attempt.")
        return jsonify({'error': 'Unauthorized'}), 401

    # Security & Validation
    if request.content_length > MAX_CHAT_PAYLOAD_SIZE:
        logging.warning(f"Chat attempt with oversized payload: {request.content_length} bytes")
        return jsonify({'error': 'Request payload too large'}), 413

    if not request.json or 'message' not in request.json:
        logging.warning("Chat attempt with missing or invalid JSON.")
        return jsonify({'error': 'Invalid request. JSON with a "message" key is required.'}), 400

    user_message = request.json['message']
    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({'error': 'Message cannot be empty.'}), 400

    try:
        # Format the current sensor data into a string to provide context to the AI
        context_data_string = (
            f"Current sensor readings are: "
            f"Nitrogen (N): {latest_sensor_data['N']}, "
            f"Phosphorus (P): {latest_sensor_data['P']}, "
            f"Potassium (K): {latest_sensor_data['K']}, "
            f"Temperature: {latest_sensor_data['temperature']:.1f}°C, "
            f"Humidity: {latest_sensor_data['humidity']:.1f}%, "
            f"pH: {latest_sensor_data['ph']:.2f}, "
            f"Rainfall: {latest_sensor_data['rainfall']:.1f}mm. "
            f"The AI model currently recommends planting: {latest_sensor_data['predicted_crop']}."
        )

        system_prompt = (
            "You are AgriBot, an expert AI assistant for farmers. Your goal is to provide "
            "concise, helpful, and actionable advice on soil health, crop management, and "
            "precision agriculture. When answering, you MUST consider the following real-time "
            f"data from the farm's sensors:\n\n{context_data_string}\n\n"
            "Base your answers on this data. For example, if asked 'what should I plant?', use the "
            "data to give a specific recommendation."
        )

        logging.info(f"Sending user message to OpenAI: '{user_message[:50]}...'")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        reply = completion.choices[0].message['content']
        logging.info("Received successful response from OpenAI.")
        return jsonify({'reply': reply})

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API Error: {e}")
        return jsonify({'error': f'The AI assistant is currently unavailable: {e}'}), 503
    except Exception as e:
        logging.error(f"An unexpected error occurred in the chat route: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

# --- Helper Functions ---
def log_to_db(data, prediction):
    """Logs a new sensor reading to the SQLite database."""
    try:
        db = get_db()
        db.execute('''
            INSERT INTO sensor_history (N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['N'], data['P'], data['K'],
            data['temperature'], data['humidity'],
            data['ph'], data['rainfall'], prediction
        ))
        db.commit()
        logging.info("Successfully logged sensor data to database.")
    except sqlite3.Error as e:
        logging.error(f"Failed to log data to database: {e}", exc_info=True)

if __name__ == '__main__':
    # Database initialization is now handled via the "flask init-db" command.
    app.run(host='0.0.0.0', port=5001, debug=True)