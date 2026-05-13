import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# 1. Define Realistic Crop Profiles
# Format: [N_min, N_max, P_min, P_max, K_min, K_max, Temp_min, Temp_max, Hum_min, Hum_max, pH_min, pH_max, Rain_min, Rain_max]
crop_profiles = {
    'Rice':       [60, 99, 35, 60, 35, 45, 20, 40, 80, 100, 5.5, 7.5, 180, 300],
    'Cotton':     [20, 40, 35, 60, 15, 25, 22, 35, 50, 70,  5.8, 8.0, 60,  110],
    'Wheat':      [20, 50, 40, 70, 20, 40, 10, 25, 40, 70,  6.0, 7.5, 40,  100],
    'Maize':      [60, 100, 35, 60, 15, 25, 18, 27, 50, 70,  5.5, 7.5, 60,  120],
    'Coffee':     [80, 120, 15, 30, 25, 35, 15, 28, 50, 90,  5.0, 7.0, 150, 250],
    'Sugarcane':  [80, 120, 35, 60, 45, 60, 20, 35, 70, 90,  6.0, 7.5, 150, 250],
    'Soybean':    [20, 40, 40, 60, 60, 80, 20, 30, 60, 70,  6.0, 7.0, 60,  100] # New crop
}

# 2. Generate the Massive Synthetic Dataset
samples_per_crop = 500  # 500 rows per crop = 3000 rows total
data = []

print(f"Generating synthetic dataset for {len(crop_profiles)} crops ({samples_per_crop} samples each)...")

for crop, ranges in crop_profiles.items():
    for _ in range(samples_per_crop):
        # Generate random values within the realistic ranges for each parameter
        N = np.random.uniform(ranges[0], ranges[1])
        P = np.random.uniform(ranges[2], ranges[3])
        K = np.random.uniform(ranges[4], ranges[5])
        Temp = np.random.uniform(ranges[6], ranges[7])
        Hum = np.random.uniform(ranges[8], ranges[9])
        pH = np.random.uniform(ranges[10], ranges[11])
        Rain = np.random.uniform(ranges[12], ranges[13])
        
        # Add a tiny bit of random noise to make the model robust
        N += np.random.normal(0, 2)
        Temp += np.random.normal(0, 1)
        pH += np.random.normal(0, 0.2)
        
        data.append([N, P, K, Temp, Hum, pH, Rain, crop])

# 3. Convert to Pandas DataFrame
columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
df = pd.DataFrame(data, columns=columns)

# Save the dataset to a CSV just in case you want to view it in Excel
df.to_csv('large_agricultural_dataset.csv', index=False)
print("Dataset generated and saved as 'large_agricultural_dataset.csv'")

# 4. Prepare Data for Machine Learning
X = df.drop('label', axis=1)  # Features (Sensor data)
y = df['label']               # Target (Crop Name)

# Split into 80% training data and 20% testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train the Random Forest Model
print("\nTraining the Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train.values, y_train) # .values strips the headers to prevent warnings later

# 6. Evaluate the Model
predictions = model.predict(X_test.values)
accuracy = accuracy_score(y_test, predictions)

print(f"\nModel Training Complete!")
print(f"Model Accuracy on Test Data: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# 7. Save the Model to be used by the Flask Server
with open('soil_model.pkl', 'wb') as file:
    pickle.dump(model, file)
    
print("\nModel successfully saved as 'soil_model.pkl'. Your Flask server is ready to use it!")