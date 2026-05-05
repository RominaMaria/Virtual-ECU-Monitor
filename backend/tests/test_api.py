import requests

def test_api_response():
    response = requests.get("http://localhost:8000/sensor-data")
    if response.status_code == 200:
        data = response.json()
        print(f"API Check: PASS. Received: {data}")
    else:
        print("API Check: FAIL. Server might be down.")
