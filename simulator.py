import requests
import time
import random

# EXACT URL of your Flask Server
URL = 'http://127.0.0.1:5000/predict'

def run_simulator():
    print("Starting IoT Simulator...")
    
    while True:
        # 1. Create synthetic data
        payload = {
            'N': random.randint(60, 100),
            'P': random.randint(35, 60),
            'K': random.randint(15, 45),
            'temperature': random.uniform(20.0, 35.0),
            'humidity': random.uniform(50.0, 80.0),
            'ph': random.uniform(5.5, 7.5),
            'rainfall': random.uniform(60.0, 200.0)
        }
        
        print(f"Attempting to send data to {URL}...")
        
        # 2. Try to send it to the server
        try:
            response = requests.post(URL, json=payload)
            
            # 3. Print the server's response
            if response.status_code == 200:
                print(f"SUCCESS! Server says: {response.json()}\n")
            else:
                print(f"FAILED! Server returned status code: {response.status_code}\n")
                
        except requests.exceptions.ConnectionError:
            print("\nERROR: Connection Refused!")
            print("Is app.py definitely running in Terminal 1?")
            print("Did you check if the URL matches exactly?\n")
            
        # Wait 3 seconds before sending the next reading
        time.sleep(3)

if __name__ == '__main__':
    run_simulator()