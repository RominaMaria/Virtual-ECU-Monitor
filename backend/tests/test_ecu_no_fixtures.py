import pytest
import os
import subprocess
import requests

def get_ecu_output():
    if os.name == 'nt':
        exe_path = "../../firmware/ecu_monitor.exe"
    else:
        exe_path = "firmware/ecu_monitor.bin"
    
    result = subprocess.run([exe_path], capture_output=True, text=True)
    return result.stdout

def test_ecu_temp_is_safe():
    output = get_ecu_output()
    # --- DYNAMIC CONFIG LOGIC ---
    # We read the same variable the Docker container uses!
    # If it's missing, we default to 120.0 as a backup.
    raw_threshold = os.getenv("TEMP_THRESHOLDS", "120.0")
    limit = float(raw_threshold)
    temp_float = None

    for line in output.split('\n'):
        if "Temperature:" in line:
            temp_val = line.split(':')[1].strip()
            temp_float = float(temp_val.replace('C', '').strip())
            break
    assert temp_float is not None, "Temperature data not found in ECU output"
    if temp_float > -90:
        assert 0.0 <= temp_float <= limit, f"Temp {temp_float} exceeds dynamic limit {limit}"

def test_ecu_status_valid():
    output = get_ecu_output()
    assert("ERROR DETECTED!" in output or "System OK" in output)


def test_api_reports_sensor_error_when_broken():
    response = requests.get("http://localhost:8000/ecu-status")
    data = response.json()
    
    assert response.status_code == 200
    assert data["status"] == "SENSOR ERROR"
    # CHANGE THIS: -999 / 10.0 is -99.9
    assert data["value"] == -99.9 
    assert "Out of physical bounds" in data["msg"]