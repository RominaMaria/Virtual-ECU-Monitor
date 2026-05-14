import pytest
import os
import subprocess
import requests
import sqlite3

@pytest.fixture
def ecu_limit():
    raw_thresholds = os.getenv("TMP_THRESHOLDS", "120.0")
    return float(raw_thresholds)    

@pytest.fixture
def raw_output():
    if os.name == 'nt':
        exe_path = "../../firmware/ecu_monitor.exe"
    else:
        exe_path = "firmware/ecu_monitor.bin"
    
    result = subprocess.run([exe_path], capture_output=True, text=True)
    return result.stdout

def test_ecu_temp_is_safe(raw_output, ecu_limit):
    # Notice how we just 'ask' for raw_output and ecu_limit as arguments!
    temp_float = None

    for line in raw_output.split('\n'):
        if "Temperature:" in line:
            temp_val = line.split(':')[1].strip()
            temp_float = float(temp_val.replace('C', '').strip())
            break
    assert temp_float is not None, "Temperature data not found in ECU output"
    if temp_float > -90:
        assert 0.0 <= temp_float <= ecu_limit, f"Temperature {temp_float}C exceeds safe limit of {ecu_limit}C"

def test_ecu_status_valid(raw_output):
    assert("ERROR DETECTED!" in raw_output or "System OK" in raw_output)


def test_api_reports_sensor_error_when_broken():
    response = requests.get("http://localhost:8000/ecu-status")
    data = response.json()
    
    assert response.status_code == 200
    assert data["status"] == "SENSOR ERROR"
    # CHANGE THIS: -999 / 10.0 is -99.9
    assert data["value"] == -99.9 
    assert "Out of physical bounds" in data["msg"]


def test_database_record_exists():
    # 1. Trigger the API
    requests.get("http://localhost:8000/ecu-status")
    db_path = "/app/backend/ecu_history.db"
    # 2. Connect to the DB manually in the test to check it
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM logs")
    count = cursor.fetchone()[0]
    conn.close()
    
    # 3. If the API worked, there should be at least 1 row
    assert count > 0

def test_data_integrity_binary_vs_db(raw_output):
    temp_float = None

    for line in raw_output.split('\n'):
        if "Temperature:" in line:
            temp_val = line.split(':')[1].strip()
            temp_float = float(temp_val.replace('C', '').strip())
            break
    conn = sqlite3.connect("/app/backend/ecu_history.db")
    last_entry = conn.execute("SELECT temp FROM logs ORDER BY timestamp DESC LIMIT 1").fetchone()[0]
    conn.close()

    assert last_entry == pytest.approx(temp_float), "Data Mismatch between Binary and Database!" 
