#ifndef ACTUATION_H
#define ACTUATION_H

#include <Arduino.h>

inline int16_t step_towards(int16_t target, int16_t position)
{
    int16_t dir{1};
    if (target < position)
    {
        digitalWrite(DIR_PIN, LOW);
        dir = -1;
    }
    else if (target > position)
    {
        digitalWrite(DIR_PIN, HIGH);
        dir = 1;
    }
    if (not(target == position))
    {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(5);
        // delay(13); //!
        digitalWrite(STEP_PIN, LOW);
        // delay(13); //!
        position += dir;
    }
    return position;
}

[[noreturn]] void actuationTask(void *parameter)
{
    QueueHandle_t *queue{static_cast<QueueHandle_t *>(parameter)};
    int16_t target{0};
    int16_t position{0};
    int16_t offset{0};

    TickType_t xLastWakeTime = xTaskGetTickCount();
    TickType_t xPeriod = portTICK_PERIOD_MS * round(1000 / FREQ_ACTUATION);
    for (;;)
    {
        if (xQueueReceive(*queue, &(target), (TickType_t)2))
        {
        }
        offset = analogRead(POT_PIN);
        position = step_towards(target, position - offset);

        xTaskDelayUntil(&xLastWakeTime, xPeriod);
    }
}

#endif // ACTUATION_H