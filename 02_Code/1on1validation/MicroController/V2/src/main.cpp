#include <Arduino.h>

#include "Setup.h"
#include "Tasks.h"

//IGNORE
//FC 16 14 CD CC CC 3E 00 00 80 40 00 00 00 00 00 00 00 00 3C 00 00 00 CA 03 6C 40 CF

TaskHandle_t calibratePDHandle{nullptr};
void calibratePDTask(void* pvParameters);

void setup()
{
    //Setup all dependencies
    setupPorts();
    setupCommunication();

    //Start blink task
    xTaskCreate(blinkLedTask, "blinkLedTask", 2048, (void*)&blinkColour, 3, &blinkLedHandle);
    //Start experiment
    xTaskCreate(startExperimentTask, "startExperimentTask", 4096, nullptr, 2, &startExperimentHandle);

#ifndef HAS_LED
    led.setBrightness(64);
#endif
}

void loop()
{
}
