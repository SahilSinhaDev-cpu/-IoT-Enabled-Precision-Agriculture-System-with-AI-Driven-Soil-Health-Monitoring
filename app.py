from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load the trained model
print(" * Loading AI Model...")
with open('soil_model.pkl', 'rb') as f:
    model = pickle.load(f)
print(" * Model loaded successfully!")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # Extract features
        features = [
            data['N'], data['P'], data['K'], 
            data['temperature'], data['humidity'], 
            data['ph'], data['rainfall']
        ]
        
        # Make prediction
        prediction = model.predict([features])[0]
        
        # Simple advisory logic
        advisory = "Standard NPK application recommended."
        if prediction == "Rice":
            advisory = "Ensure field is flooded to 5cm."
        elif prediction == "Maize":
            advisory = "Ensure good drainage. Apply Zinc if needed."

        response = {
            'predicted_crop': prediction,
            'advisory': advisory,
            'status': 'success'
        }
        
        # Print to terminal so it shows in screenshot
        print(f"Received: {features} -> Prediction: {prediction}")
        
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)