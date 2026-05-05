import os
import subprocess

def run_ecu_validation():
    # Detect environment: Docker/Linux vs Windows
    if os.name == 'nt':
        exe_path = "../../firmware/ecu_monitor.exe"
    else:
        # Inside the Docker container, we are in /app
        # The binary is at /app/firmware/ecu_monitor.bin
        exe_path = "firmware/ecu_monitor.bin"
    
    print(f"--- Starting Validation on {exe_path} ---")

    try:
        # 2. Execute the C++ program and "pipe" the output to Python
        # capture_output=True grabs what std::cout printed
        # text=True converts bytes to a Python string automatically
        result = subprocess.run([exe_path], capture_output=True, text=True)
        
        # 3. Analyze the data (The "Logic" Layer)
        output = result.stdout
        print("Captured Output:\n" + output)

        # 4. Perform the "Assertions" (Testing if the system is safe)
        if "ERROR DETECTED!" in output:
            print("Test Result: PASS (System correctly identified the error bit)")
        else:
            print("Test Result: FAIL (System missed the error status)")
        if "INACTIVE!" in output:
            print("Test result: PASS")
        else:
            print("Test result: FAILED")

        # 5. Extract specific data
        # We look for the temperature line and pull the number
        for line in output.split('\n'):
            if "Temperature:" in line:
                temp_val = line.split(':')[1].strip()
                print(f"Extracted Temperature for Log: {temp_val}")
                temp_float = float(temp_val.replace('C', '').strip())
                if 0.0 <= temp_float <= 120.0:
                    print(f"Safety Check: PASS (Temp {temp_float} is within safe operating range)")
                else:
                    print(f"Safety Check: FAIL (CRITICAL: Temp {temp_float} out of bounds!)")
            

    except FileNotFoundError:
        print("Error: Could not find ecu_monitor.exe. Did you compile it in the firmware folder?")

if __name__ == "__main__":
    run_ecu_validation()