import requests
import os

# Base URL for the hardware service
# Reads from environment variable or defaults to localhost:5002
BASE_URL = os.getenv('HARDWARE_SERVICE_URL', 'http://localhost:5002')

def test_get_hw_info():
    """Test getting hardware information"""
    url = f"{BASE_URL}/get_hw_info"
    params = {"hwSetName": "HWSet1"}
    response = requests.get(url, params=params)
    
    print("Status Code:", response.status_code)
    try:
        print("RESPONSE JSON:", response.json())
        if response.status_code == 200:
            print("✅ Hardware retrieved successfully.")
        elif response.status_code == 404:
            print("ℹ️ Hardware not found.")
        else:
            print("❌ Unexpected status code:", response.status_code)
    except requests.exceptions.JSONDecodeError:
        print("❌ Response is not valid JSON")
        print("RAW RESPONSE:", response.text)

if __name__ == "__main__":
    test_get_hw_info()

