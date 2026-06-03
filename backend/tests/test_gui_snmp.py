import pytest
import threading
import time
import tkinter as tk

class MockDeviceDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("R&S Mock Device Screen")
        self.root.geometry("400x200")
        
        # Bring the window to the absolute front of your desktop
        self.root.attributes('-topmost', True)
        
        self.frequency_label = tk.Label(
            self.root, 
            text="Status: Idle (0 MHz)", 
            font=("Arial", 16), 
            fg="blue"
        )
        self.frequency_label.pack(pady=60)

        self.voltage_label = tk.Label(
            self.root,
            text="Status Voltage: Normal (230 V)",
            font=("Arial", 16),
            fg="black" 
        )
        self.voltage_label.pack(pady=10)

    def simulate_snmp_network_packet(self, new_freq):
        """Simulates receiving an SNMP packet via the Ethernet port."""
        # Use root.after to safely update UI elements from a background thread
        self.root.after(0, lambda: self.frequency_label.config(text=f"Status: Active ({new_freq} MHz)"))
        print(f"[DISPLAY HARDWARE] UI text property updated to: {new_freq} MHz")

    def simulate_snmp_network_trafic_voltage(self, new_voltage):
        self.root.after(0, lambda: self.voltage_label.config(text=f"Status Voltage: Changed ({new_voltage} V )"))
        print(f"[DISPLAY HARDWARE] UI text property for voltage uüdate to: {new_voltage} V")


# --- THIS FUNCTION RUNS THE AUTOMATION STEPS IN THE BACKGROUND ---
def run_automation_sequence(device_ui):
    try:
        print("\n[WATCH SCREEN] Look at your desktop! Window is open. Waiting 2.5 seconds...")
        time.sleep(2.5)

        target_frequency = 100
        target_voltage = 50
        print("[TEST RUNNER] Sending SNMP SET Command for frequency and voltage... ")
        device_ui.simulate_snmp_network_packet(target_frequency)
        device_ui.simulate_snmp_network_trafic_voltage(target_voltage)

        print("[WATCH SCREEN] Text changed to 100 MHz for freq and 50 for Voltage Keeping it open for 3 seconds...")
        time.sleep(3.0)

        # Read property directly from memory
        actual_ui_text = device_ui.frequency_label.cget("text")
        print(f"[TEST RUNNER] Read property from GUI WIDGET object: '{actual_ui_text}'")

        actual_ui_text_voltage = device_ui.cget("text")
        print(f"[TEST RUNNER] Read properties from GUI WIDGET object: '{actual_ui_text_voltage}")

        assert f"{target_frequency} MHz" in actual_ui_text
        print(f"[TEST RUNNER] Assertion Successfully Frontend matches Backend")

        assert f"{target_voltage} V" in actual_ui_text_voltage
        print(f"[TEST RUNNER] Assertion Successfully Frontend matches Backend")

    finally:
        print("[TEST RUNNER] Shutting down simulation window...")
        device_ui.root.after(0, device_ui.root.destroy)


def test_ethernet_command_updates_ui_property():
    # 1. Initialize the display on the MAIN THREAD
    device_ui = MockDeviceDisplay()

    # 2. Start the test runner sequence inside a background thread
    test_thread = threading.Thread(target=run_automation_sequence, args=(device_ui,))
    test_thread.start()

    # 3. Start the visual window loop on the main thread (Forces Windows to render it!)
    device_ui.root.mainloop()
    
    # Wait for the test thread to complete its assertions
    test_thread.join()