
#define FREQ_ACTUATION 200   // Hz
#define FREQ_ACQUISITION 200 // Hz
#define FREQ_LED 30          // Hz

#include "Setup.h"

#include "actuation.h"
#include "acquisition.h"

void setup()
{
    // INIT PINS
    pinMode(DIR_PIN, OUTPUT);
    pinMode(STEP_PIN, OUTPUT);
    pinMode(POT_PIN, ANALOG);

    // INIT RTOS TASKS
    int16_t initTarget{0};
    static QueueHandle_t queue{xQueueCreate(1, sizeof(int16_t))};

    if (queue == 0)
    {
        for (;;)
        {
        }
    }
    xQueueSend(queue, &initTarget, (TickType_t)2);

    xTaskCreatePinnedToCore(&actuationTask, "actuationTask", 2048, (void *)&queue, 10, &actuationHandle, 0);
    xTaskCreate(&acquisitionTask, "acquisitionTask", 262144, (void *)&queue, 23, &acquisitionHandle);
}

void loop()
{
}