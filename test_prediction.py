#!/usr/bin/env python3

import requests
import json

# Test the prediction endpoint
try:
    print("Testing prediction endpoint...")
    
    payload = {
        "magnitude": 5.2,
        "depth_km": 10,
        "latitude": 19.07,
        "longitude": 72.86
    }
    
    print(f"Sending payload: {json.dumps(payload)}")
    
    response = requests.post(
        'http://127.0.0.1:8000/predict/custom',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Prediction: {data.get('predicted_alert', 'N/A')}")
        print(f"Confidence: {data.get('confidence', 'N/A')}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Request failed: {e}")
