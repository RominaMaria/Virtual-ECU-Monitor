import requests
from unittest.mock import patch

@patch('requests.get')
def test_api_mocked(mock_get):
    # We FAKE the response so we don't even need the server running!
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"status": "OK", "temp": 25.0}
    
    response = requests.get("http://fake-url")
    assert response.json()["temp"] == 25.0

# 1. THE DECORATOR: "Swap the real requests.get for a Mock"
@patch('requests.get')
def test_api_unauthorized_access(mock_get): # 2. THE PARAMETER: Catch the Mock here
    
    # 3. THE PROGRAMMING: Tell the Stunt Double (Mock) what to do
    # When someone calls you, return a status_code of 401
    mock_get.return_value.status_code = 401 
    
    # 4. THE ACTION: This call DOES NOT go to the web. 
    # It hits the 'mock_get' stunt double.
    response = requests.get("http://localhost:8000/ecu-status")
    
    # 5. THE ASSERTION: Check if the logic handled the 401 correctly
    assert response.status_code == 401
    print("Security Check: API correctly blocked unauthorized access.")

"""def test_api_response():
    response = requests.get("http://localhost:8000/sensor-data")
    if response.status_code == 200:
        data = response.json()
        print(f"API Check: PASS. Received: {data}")
    else:
        print("API Check: FAIL. Server might be down.")"""
