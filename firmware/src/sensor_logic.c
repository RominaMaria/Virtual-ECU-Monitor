#include "sensor_types.h"
#include <time.h>
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