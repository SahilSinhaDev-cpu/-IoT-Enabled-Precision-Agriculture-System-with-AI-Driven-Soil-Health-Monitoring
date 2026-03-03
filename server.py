from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the AI Model
try:
    model = joblib.load('soil_model.pkl')
    print("AI Model loaded.")
except:
    print("ERROR: Run train_ai.py first!")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Get JSON data
        data = request.get_json()
        
        # 2. Extract features
        features = [
            data.get('N'), 
            data.get('P'), 
            data.get('K'), 
            data.get('temperature'), 
            data.get('humidity'), 
            data.get('ph'), 
            data.get('rainfall', 100.0) # Default if missing
        ]
        
        # 3. Predict
        input_data = np.array([features])
        prediction = model.predict(input_data)[0]
        
        # 4. Generate Advice
        advice = "Soil conditions optimal."
        if prediction == 'Rice': advice = "Keep soil submerged. Monitoring water level."
        if prediction == 'Cotton': advice = "Ensure good drainage. Watch for pests."
        
        # 5. Respond
        return jsonify({
            'status': 'success',
            'crop': prediction,
            'advice': advice
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)