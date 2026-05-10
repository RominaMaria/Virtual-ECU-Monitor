from fastapi import FastAPI
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


# Add this right after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow everything for our project
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    try:
        # We search line by line to find the actual temperature line
        temp_value = None
        for line in raw_output.split('\n'):
            if "Temperature:" in line:
                # Extracts "-99.9" from "Temperature: -99.9 C"
                temp_value = line.split("Temperature:")[1].replace("C", "").strip()
                break
        
        if temp_value is None:
            raise ValueError("Could not find Temperature string")

        temp = float(temp_value)

        if temp < -50 or temp > 150:
            return {"status": "SENSOR ERROR", "value": temp, "msg": "Out of physical bounds"}
        
        return {"status": "OK", "temp": temp}

    except Exception as e:
        # If we see 'CRITICAL_FAILURE' in Jenkins, it means the parsing above failed
        return {"status": "CRITICAL_FAILURE", "msg": f"Parsing error: {str(e)}"}
    