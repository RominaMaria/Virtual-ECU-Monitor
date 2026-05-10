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

def run_ecu_validation():
    if os.name == 'nt':
        exe_path = "../../firmware/ecu_monitor.exe"
    else:
        exe_path = "firmware/ecu_monitor.bin"
    
    try:
        # 1. Run the live C++ code
        result = subprocess.run([exe_path], capture_output=True, text=True)
        output = result.stdout
        
        # 2. Extract live data
        for line in output.split('\n'):
            if "Temperature:" in line:
                # Get the string '28.3 C' -> turn into float 28.3
                temp_val = line.split(':')[1].strip()
                temp_float = float(temp_val.replace('C', '').strip())
                
                # 3. PASS THE LIVE DATA to the separate function
                validate_temperature_range(temp_float)
                
    except Exception as e:
        print(f"Error during validation: {e}")

if __name__ == "__main__":
    run_ecu_validation()