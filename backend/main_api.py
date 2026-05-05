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
@app.get("/sensor-data")
def get_sensor_data():
    # Detect if we are on Windows or Linux
    if os.name == 'nt':
        exe_path = os.path.abspath("../firmware/ecu_monitor.exe")
    else:
        # This is for Docker/Linux
        exe_path = os.path.abspath("firmware/ecu_monitor.bin")

    result = subprocess.run([exe_path], capture_output=True, text=True)

    # We parse the output into a "JSON" object (which the Web understands)
    output = result.stdout
    data = {
        "sensor_id": 1,
        "temperature": 0.0,
        "status": "OK"
    }

    for line in output.split('\n'):
        if "Temperature" in line:
            data["temperature"] = float(line.split(':')[1].replace('C', '').strip())
            if "ERROR" in line:
                data["status"] = "ERROR"
    return data