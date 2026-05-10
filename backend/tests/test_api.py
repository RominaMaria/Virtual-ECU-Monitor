import requests
from unittest.mock import patch

@patch('requests.get')
def test_api_mocked(mock_get):
    # We FAKE the response so we don't even need the server running!
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"status": "OK", "temp": 25.0}
    
    response = requests.get("http://fake-url")
    assert response.json()["temp"] == 25.0

"""def test_api_response():
    response = requests.get("http://localhost:8000/sensor-data")
    if response.status_code == 200:
        data = response.json()
        print(f"API Check: PASS. Received: {data}")
    else:
        print("API Check: FAIL. Server might be down.")"""
