import requests
import json

url = "http://127.0.0.1:8002/v1/locations/1"
try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
