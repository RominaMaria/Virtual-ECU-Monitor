from fastapi import FastAPI
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
app = FastAPI()


# Add this right after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow everything for our project
    allow_methods=["*"],
    allow_headers=["*"],
)

# This gets the directory where main_api.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ecu_history.db")
# Initialize the DB (The "Logbook")
def init_db():
    # 1. Connect (or create): This opens the file 'ecu_history.db'. 
    # If it doesn't exist, SQLite creates it automatically.
    conn = sqlite3.connect(DB_PATH)
    
    # 2. Cursor: Think of this as the "Pen" you use to write in the logbook.
    cursor = conn.cursor()
    
    # 3. Execute: This is the SQL command. 
    # 'CREATE TABLE IF NOT EXISTS' ensures we don't crash if the DB already exists.
    # We define 3 columns:
    # - timestamp: Automatically records WHEN the reading happened.
    # - temp: Stores the number (REAL is SQL for float).
    # - status: Stores text like 'OK' or 'SENSOR ERROR'.
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                      (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                       temp REAL, status TEXT)''')
    
    # 4. Commit: This "Saves" the changes permanently to the disk.
    conn.commit()
    
    # 5. Close: Always close the logbook so other processes (like your Tests) can read it.
    conn.close()

init_db()


def call_cpp_binary():
    # Detect if we are on Windows or Linux
    if os.name == 'nt':
        exe_path = os.path.abspath("../firmware/ecu_monitor.exe")
    else:
        # This is for Docker/Linux
        exe_path = os.path.abspath("firmware/ecu_monitor.bin")
    result = subprocess.run([exe_path], capture_output=True, text=True)
    return result.stdout

@app.get("/sensor-data")
def get_sensor_data():  

    output = call_cpp_binary()
    data = {
        "sensor_id": 1,
        "temperature": 0.0,
        "status": "OK"
    }

    for line in output.split('\n'):
        if "Temperature" in line:
            data["temperature"] = float(line.split(':')[1].replace('C', '').strip())
            if "SENSOR ERROR" in line:
                data["status"] = "SENSOR ERROR"
    return data

@app.get("/ecu-status")
def get_status():
    raw_output = call_cpp_binary().strip() 
    print(f"DEBUG_DATA: '{raw_output}'")
    try:
        # --- 1. Your existing parsing logic ---
        temp_value = None
        for line in raw_output.split('\n'):
            line = line.strip() # Remove hidden spaces
            if "Temperature:" in line:
                # This split is safer
                temp_value = line.split("Temperature:")[1].replace("C", "").strip()
                break
        
        if temp_value is None:
            raise ValueError("Could not find Temperature string")
        temp = float(temp_value)

        # --- 2. Determine the Logic result ---
        if temp < -50 or temp > 150:
            final_status = "SENSOR ERROR"
            response = {"status": final_status, "value": temp, "msg": "Out of physical bounds"}
        else:
            final_status = "OK"
            response = {"status": final_status, "temp": temp}

        # --- 3. THE TRANSITION: Database Logging ---
        # We do this AFTER the logic, but BEFORE the return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (temp, status) VALUES (?, ?)", (temp, final_status))
        conn.commit()
        conn.close()

        return response

    except Exception as e:
        return {"status": "CRITICAL_FAILURE", "msg": f"Parsing error: {str(e)}"}