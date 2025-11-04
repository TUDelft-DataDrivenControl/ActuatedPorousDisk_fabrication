#ifndef ACTUATION_H
#define ACTUATION_H

// https://esp32tutorials.com/esp32-esp-idf-freertos-xQueue-tutorial/

#include <Arduino.h>
#include <queue>

inline int16_t step_towards(int16_t tar, int16_t pos)
{
    // For timing see section 7.6 of drv8825 docs
    // https://www.ti.com/lit/ds/symlink/drv8825.pdf
    int16_t dir{0};
    if (tar > pos)
    {
        digitalWrite(DIR_PIN, LOW);
        delayMicroseconds(5); // Setup time
        dir = 1;
    }
    else if (tar < pos)
    {
        digitalWrite(DIR_PIN, HIGH);
        delayMicroseconds(5); // Setup time
        dir = -1;
    }

    if (not(tar == pos))
    {
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(5); // Pulse time
        // delay(150);            //!
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(5); // Pulse time
        // delay(150);            //!
    }
    return dir;
}

[[noreturn]] void actuationTask(void *parameter)
{
    QueueHandle_t *xQueue{static_cast<QueueHandle_t *>(parameter)};
    int16_t target{0};
    int16_t position{0};

    TickType_t xLastWakeTime = xTaskGetTickCount();
    TickType_t xPeriod = portTICK_PERIOD_MS;
    std::queue<int16_t> offset_queu;
    for (;;)
    {
        if (xQueueReceive(*xQueue, &(target), (TickType_t)2))
        {
        }

        int16_t potread = (int16_t)(map(analogRead(POT_PIN), (4096 / 2), (4096 / 1), -213, 213));
        offset_queu.push(potread);
        while (offset_queu.size() > 50)
        {
            offset_queu.pop();
        }

        std::queue<int16_t> offset = offset_queu;
        while (offset.size() > 1)
        {
            offset.back() += offset.front();
            offset.pop();
        }
        offset.back() /= (int16_t)(offset_queu.size());

        position += step_towards(target, position - offset.back());

        // Serial.print("Pot trim: ");
        // Serial.print(offset.back());
        // Serial.print(" , Current pos: ");
        // Serial.print(position);
        // Serial.print(" , Set target:");
        // Serial.println(target);

        xTaskDelayUntil(&xLastWakeTime, xPeriod);
    }
}

#endif // ACTUATION_H