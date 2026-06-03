import os
import subprocess
import pytest

# --- SEPARATE SAFETY FUNCTION ---
def validate_temperature_range(temp):
    """Business logic: Is this temperature safe for an engine?"""
    if 0.0 <= temp <= 120.0:
        print(f"Safety Check: PASS (Temp {temp}C is within safe range)")
        return True
    else:
        print(f"Safety Check: FAIL (CRITICAL: Temp {temp}C out of bounds!)")
        return False

def raw_output():
    if os.name == 'nt':
        exe_path = "../../firmware/ecu_monitor.exe"
    else:
        exe_path = "firmware/ecu_monitor.bin"
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"CRITICAL: Firmware binary missing at {exe_path}")
    result = subprocess.run([exe_path], capture_output=True, text=True)
    return result.stdout

def run_ecu_validation():

    try:
        output = raw_output()
        for line in output.split('\n'):
            if "Temperature:" in line:
                temp_val = line.split(':')[1].strip()
                temp_float = float(temp_val.replace('C', '').strip())
                validate_temperature_range(temp_float)
                
    except Exception as e:
        print(f"Error during validation: {e}")


if __name__ == "__main__":
    run_ecu_validation()