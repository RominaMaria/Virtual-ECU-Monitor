import pytest
import os
import subprocess
import requests
import sqlite3
import time


@pytest.fixture
def current_mode():
    return os.getenv("ECU_MODE", "STRICT")


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
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"CRITICAL: Firmware binary not found at {exe_path}")
    result = subprocess.run([exe_path], capture_output=True, text=True)
    return result.stdout

@pytest.mark.requirement("REQ-ECU-001-MODE-CONTROL")
def test_ecu_behavior_by_mode(current_mode, ecu_limit, record_property, base_url):
    # Trigger teh API
    record_property("requirement_id", "REQ-ECU-001-MODE-CONTROL")
    response = requests.get(f"{base_url}/ecu-status?mode={current_mode}")
    data = response.json()
    # Logic: What should happen in this specific mode?
    if current_mode == "BROKEN":
        assert data["status"] == "SENSOR ERROR"
        assert data["value"] == -99.9
    
    elif current_mode == "STRICT":
        assert data ["status"] == "OK"
        assert 0.0 <= data["temp"] <= ecu_limit, f"Temp {data['temp']} exceeds limit {ecu_limit}"

    elif current_mode == "SIMULATION":
        assert data["status"] == "OK"
        # In simulation, maybe we always expect exactly 25.0
        assert data["temp"] == 25.0

@pytest.mark.requirement("REQ-ECU-002-THERMAL-SAFETY")
def test_ecu_temp_is_safe(raw_output, ecu_limit, record_property):
    # Notice how we just 'ask' for raw_output and ecu_limit as arguments!
    record_property("requirement_id", "REQ-ECU-002-THERMAL-SAFETY")
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


def test_api_reports_sensor_error_when_broken(current_mode, base_url):
    response = requests.get(f"{base_url}/ecu-status?mode={current_mode}")
    data = response.json()
    if current_mode == "BROKEN":
        assert response.status_code == 200
        assert data["status"] == "SENSOR ERROR"
        # CHANGE THIS: -999 / 10.0 is -99.9
        assert data["value"] == -99.9 
        assert "Out of physical bounds" in data["msg"]
    else:
        pytest.skip("Skipping this test because ECU_MODE is not set to BROKEN")


def test_database_record_exists(base_url):
    # 1. Trigger the API
    requests.get(f"{base_url}/ecu-status")
    db_path = "/app/backend/ecu_history.db"
    # 2. Connect to the DB manually in the test to check it
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM logs")
    count = cursor.fetchone()[0]
    conn.close()
    
    # 3. If the API worked, there should be at least 1 row
    assert count > 0

@pytest.mark.requirement("REQ-ECU-003-DATA-INTEGRITY")
def test_data_integrity_binary_vs_db(raw_output, current_mode, record_property, base_url):
    record_property("requirement_id", "REQ-ECU-003-DATA-INTEGRITY")
    # 1. Trigger the API using the correct mode parameter
    requests.get(f"{base_url}/ecu-status?mode={current_mode}")
    timeout = 2.0
    start_time = time.time() # this is frozen
    
    temp_float = None
    for line in raw_output.split('\n'):
        if "Temperature:" in line:
            temp_val = line.split(':')[1].strip()
            temp_float = float(temp_val.replace('C', '').strip())
            break
    
    # 2. Connect to the SQLite DB to fetch that fresh record
    while time.time() - start_time < timeout:
        conn = sqlite3.connect("/app/backend/ecu_history.db")
        last_entry = conn.execute("SELECT temp FROM logs ORDER BY timestamp DESC LIMIT 1").fetchone()[0]
        conn.close()
        
        # 3. Determine the expected value matching the backend logic
        if current_mode == "BROKEN":
            expected_temp = -99.9
        elif current_mode == "SIMULATION":
            expected_temp = 25.0
        else:
            expected_temp = temp_float
        time.sleep(0.05) # Wait a tiny bit before trying again
    
    assert last_entry == pytest.approx(expected_temp), "Data Mismatch between Binary and Database!"


def test_database_integrity(current_mode, base_url):
    db_path = "/app/backend/ecu_history.db"
    
    # 1. Trigger the API
    requests.get(f"{base_url}/ecu-status?mode={current_mode}")
    
    # 2. 🛠️ SMART POLLING LOOP (Max 2 seconds, check every 0.05 seconds)
    timeout = 2.0
    start_time = time.time()
    db_status = None
    
    while time.time() - start_time < timeout:
        conn = sqlite3.connect(db_path)
        last_raw = conn.execute("SELECT temp, status FROM logs ORDER BY timestamp DESC LIMIT 1").fetchone()
        conn.close()
        
        if last_raw:
            db_temp, db_status = last_raw
            # If we are in BROKEN mode and the row finally updated to SENSOR ERROR, break early!
            if current_mode == "BROKEN" and db_status == "SENSOR ERROR":
                break
            # If we are in STRICT/SIM and it says OK, break early!
            elif current_mode != "BROKEN" and db_status == "OK":
                break
                
        time.sleep(0.05) # Wait a tiny bit before trying again

    # 3. Final Assertion
    if current_mode == "BROKEN":
        assert db_status == "SENSOR ERROR", f"Expected SENSOR ERROR but got {db_status}"
    else:
        assert db_status == "OK", f"Expected OK but got {db_status}"