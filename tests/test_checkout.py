import requests
import os

# Base URL for the hardware service
# Reads from environment variable or defaults to localhost:5002
BASE_URL = os.getenv('HARDWARE_SERVICE_URL', 'http://localhost:5002')

def test_check_out():
    """Test checking out hardware"""
    url = f"{BASE_URL}/check_out"
    payload = {
        "projectId": "project123",
        "hwSetName": "HWSet1",
        "qty": 5
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    
    print("Status Code:", response.status_code)
    try:
        print("RESPONSE JSON:", response.json())
        if response.status_code == 200:
            print("✅ Hardware checked out successfully.")
        else:
            print("❌ Checkout failed with status:", response.status_code)
    except requests.exceptions.JSONDecodeError:
        print("❌ Server returned non-JSON response")
        print("Raw response:", response.text)

if __name__ == "__main__":
    test_check_out()

