#ifndef DEBUG_ROUTINES_H
#define DEBUG_ROUTINES_H

#include <Arduino.h>

#include "Setup.h"
#include "blinkLED.h"

// inline void loop_builtin_led()
// {
//     setBlinkColour(0x00000000);
//     vTaskDelay(500 / portTICK_PERIOD_MS);
//     setBlinkColour(0xFF000000);
//     vTaskDelay(333 / portTICK_PERIOD_MS);
//     setBlinkColour(0x00FF0000);
//     vTaskDelay(333 / portTICK_PERIOD_MS);
//     setBlinkColour(0x0000FF00);
//     vTaskDelay(333 / portTICK_PERIOD_MS);
//     setBlinkColour(0x000000FF);
//     vTaskDelay(333 / portTICK_PERIOD_MS);
// }

inline void test_debug_leds()
{
    digitalWrite(DIR_PIN, HIGH);
    digitalWrite(STEP_PIN, LOW);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    digitalWrite(DIR_PIN, LOW);
    digitalWrite(STEP_PIN, HIGH);
    vTaskDelay(500 / portTICK_PERIOD_MS);
}

inline void stepper_sawtooth(void *parameter)
{
    QueueHandle_t *queue{static_cast<QueueHandle_t *>(parameter)};

    for (int16_t Target1 = 0; Target1 < 5; Target1++)
    {
        xQueueSend(*queue, &Target1, (TickType_t)0);
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }
    for (int16_t Target2 = 5; Target2 > 0; Target2--)
    {
        xQueueSend(*queue, &Target2, (TickType_t)0);
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }
}

inline void test_serial_com()
{
    Serial.println("Hi, I am alive!");
    delay(1000);
    while (Serial.available())
    {
        Serial.print(Serial.read());
        Serial.print(", ");
        if (!Serial.available())
        {
            Serial.println("");
        }
    }
}

[[noreturn]] void receive_store_send(void *parameter)
{
    for (;;)
    {
        if (Serial.available() >= 8)
        {
            delay(1);
            Serial.println("COMM START");

            // Receive encoded uint64_t array length of incoming data
            byte data_length_encoded[8];
            int bytesRead = Serial.readBytes(data_length_encoded, 8);

            // Decode array length
            uint64_t data_length{(((uint64_t)(((uint8_t *)(data_length_encoded))[0]) << 0) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[1]) << 8) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[2]) << 16) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[3]) << 24) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[4]) << 32) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[5]) << 40) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[6]) << 48) +
                                  ((uint64_t)(((uint8_t *)(data_length_encoded))[7]) << 56))};

            // uint64_t data_length = *((uint64_t *)data_length_encoded);
            Serial.print("Array length received: ");
            Serial.println(data_length);

            // Receive encoded input
            byte input_buffer_encoded[data_length * 2]; // 2 bytes per int16_t
            uint64_t i = 0;
            while (Serial.available())
            {
                int bytesRead = Serial.readBytes(&input_buffer_encoded[i], 1);
                i++;
                delay(1);
            }
            Serial.println("READ OK");

            // Decode input
            int16_t input[data_length];
            uint64_t k = 0;
            for (uint64_t i = 0; i < data_length * 2; i += 2)
            {
                input[k] = (((int16_t)(((uint8_t *)(input_buffer_encoded))[i]) << 0) +
                            ((int16_t)(((uint8_t *)(input_buffer_encoded))[i + 1]) << 8));
                // *((uint16_t *)(input_buffer_encoded[i + 1] << 8 + input_buffer_encoded[i] << 0));

                k++;
            }

            // Send back input
            for (int i = 0; i < data_length; i++)
            {
                Serial.println(input[i]);
            }
            Serial.println("SENT OK");
        }
    }
}

#endif // DEBUG_ROUTINES_H