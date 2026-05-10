#include <iostream>

extern "C" {
    #include "sensor_types.h"
    #include "sensor_logic.h"
    // These MUST match the .c file exactly
    void init_sensor(EngineData *data); 
    void set_error(EngineData *data);
}

int main() {
    EngineData mySensor;
    init_sensor(&mySensor);

    std::cout << "--- ECU Monitor Initialized ---" << std::endl;
    std::cout << "Sensor ID: " << (int)mySensor.sensor_id << std::endl;
    std::cout << "Temperature: " << read_raw_sensor_data() / 10.0 << " C" << std::endl;
    //std::cout << "Engine Speed: " << mySensor.rpm << std::endl;

    set_error(&mySensor);

    if (mySensor.status & STATUS_ERROR) {
        std::cout << "Status: ERROR DETECTED!" << std::endl;
    }

    return 0;
}