#include "sensor_types.h"
#include <time.h>
#include <stdlib.h>  // Required for getenv
#include <string.h>  // Required for strcmp

void init_sensor(EngineData *data) {   
    // Get the current "Timestamp" (seconds since 1970)
    time_t seconds = time(NULL);
    int blink = seconds % 2;
    int status_index = seconds % 4;
    int base_temp = 200;
    // Use the seconds to create a moving temperature
    // (seconds % 100) will give us a number between 0 and 99
    // So the temp will be between 20.0 and 29.9
    int variance = (int)(seconds % 100);
    data->sensor_id = 0x01;
    
    data->temperature = base_temp + variance;
    data->status = STATUS_ACTIVE;

}

void set_error(EngineData *data) {
    data->status |= STATUS_ERROR;
}

//Fault Injection: Simulate a sensor failure by returning an impossible value
int read_raw_sensor_data() {
    // 1. We ask the Operating System (Linux inside Docker) for a variable named "ECU_MODE"
    char* mode = getenv("ECU_MODE");

    // 2. We check if the variable actually exists (is not NULL) 
    // AND if the text inside that variable is exactly "BROKEN"
    if ((mode != NULL) && (strcmp(mode, "BROKEN") == 0)) {
        // 3. If it is "BROKEN", we return an impossible value to simulate a hardware failure
        return -999; // Simulate a broken sensor
    }
    
    // 4. Otherwise, the "sensor" works normally and returns a realistic temperature
    return 35; // Normal operation
}