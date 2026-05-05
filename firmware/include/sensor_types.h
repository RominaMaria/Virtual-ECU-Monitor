//These 2 above are the header guards to prevent multiple inclusions of this header 
//file, which can cause compilation errors. The unique name (SENSOR_TYPES_H) 
//is used to ensure that the contents of this file are only included once during compilation.
#ifndef SENSOR_TYPES_H
#define SENSOR_TYPES_H

#include <stdint.h>

/**
 * @brief Structure representing the raw engine sensor data.
 * This matches the data format we will send to our Python middleware.
 */

typedef struct{
   uint8_t sensor_id;    //Unique ID (e.g., 0x01 for Engine)
   int16_t temperature;  //Temperature in 0.1 C (e.g., 850 = 85.0 C)
   uint16_t rpm;         //Engine speed (e.g., 3000)
   uint8_t status;       //Bit-field for status flags (e.g., 0x00 = OK, 0x01 = Warning, 0x02 = Error)
} EngineData;

#define STATUS_ACTIVE 0x01
#define STATUS_ERROR  0x02

#endif