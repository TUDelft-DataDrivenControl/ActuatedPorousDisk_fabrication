#ifndef AQUISITION_H
#define AQUISITION_H

// Decoding
inline int16_t byte2int16(byte enc[2])
{
    return (((int16_t)(((uint8_t *)(enc))[0]) << 0) +
            ((int16_t)(((uint8_t *)(enc))[1]) << 8));
}

inline int64_t byte2int64(byte enc[8])
{
    return (((uint64_t)(((uint8_t *)(enc))[0]) << 0) +
            ((uint64_t)(((uint8_t *)(enc))[1]) << 8) +
            ((uint64_t)(((uint8_t *)(enc))[2]) << 16) +
            ((uint64_t)(((uint8_t *)(enc))[3]) << 24) +
            ((uint64_t)(((uint8_t *)(enc))[4]) << 32) +
            ((uint64_t)(((uint8_t *)(enc))[5]) << 40) +
            ((uint64_t)(((uint8_t *)(enc))[6]) << 48) +
            ((uint64_t)(((uint8_t *)(enc))[7]) << 56));
}

[[noreturn]] void acquisitionTask(void *parameter)
{
    TickType_t xLastWakeTime = xTaskGetTickCount();
    TickType_t xPeriod = portTICK_PERIOD_MS * round(1000 / FREQ_ACQUISITION);

    // INIT LED
    Adafruit_NeoPixel led{1, LED_PIN, NEO_RGB + NEO_KHZ800};
    led.begin();
    led.setBrightness(10); // 0 to 255 brightest
    led.setPixelColor(0, 0x00FF8000);
    led.show();

    // INIT SERIAL
    Serial.begin(115200);
    while (!Serial)
    {
        led.setPixelColor(0, 0x00FF0000);
        led.show();
        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
        led.setPixelColor(0, 0x00000000);
        led.show();
        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
    }

    led.setPixelColor(0, 0x00FF8000);
    led.show();

    QueueHandle_t *queue{static_cast<QueueHandle_t *>(parameter)};

    Adafruit_ADS1115 ads;
    while (!ads.begin())
    {
        led.setPixelColor(0, 0x00FF0000);
        led.show();
        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
        led.setPixelColor(0, 0x00000000);
        led.show();
        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
    }
    ads.setGain(GAIN_TWOTHIRDS);
    ads.setDataRate(RATE_ADS1115_860SPS);

    led.setPixelColor(0, 0x0000FF00);
    led.show();
    Serial.println("BOOT OK");
    for (;;)
    {
        // Wait for 4 bytes of CMD
        if (Serial.available() >= 4)
        {
            vTaskDelay(100 / portTICK_PERIOD_MS);
            // delay(1);
            led.setPixelColor(0, 0x000000FF);
            led.show();
            Serial.println("COMM START");

            // Receive CMD
            char CMD[4];
            int bytesRead = Serial.readBytes(CMD, 4);

            // Serial.print("CMD received: ");
            // for (char c : CMD)
            // {
            //     Serial.print(c);
            // }
            // Serial.println();

            if (*(int *)(CMD) == *(int *)("GOTO"))
            {
                Serial.println("GOTO RECEIVED");
                // Receive target int16_t
                byte target_encoded[2];
                int bytesRead = Serial.readBytes(target_encoded, 2);
                // Echo target
                Serial.println(*target_encoded);
                // Decode target
                int16_t target = byte2int16(target_encoded);

                // Set target
                xQueueSend(*queue, &target, (TickType_t)2);
                Serial.println("GOTO COMPLETE");
            }
            else if (*(int *)(CMD) == *(int *)("STRT"))
            {
                Serial.println("STRT RECEIVED");
                // Receive operation mode
                char opmode[4];
                bytesRead = Serial.readBytes(opmode, 4);

                // for (char c : opmode)
                // {
                //     Serial.print(c);
                // }
                // Serial.println();

                if (*(int *)(opmode) == *(int *)("STAT"))
                {
                    Serial.println("STAT RECEIVED");
                    // Receive duration uint64_t and target int16_t
                    byte duration_encoded[8];
                    bytesRead = Serial.readBytes(duration_encoded, 8); // Read
                    int16_t duration = byte2int64(duration_encoded);   // Decode
                    Serial.println(duration);                          // Echo

                    byte target_encoded[2];
                    bytesRead = Serial.readBytes(target_encoded, 2); // Read
                    int16_t target = byte2int16(target_encoded);     // Decode
                    Serial.println(target);                          // Echo

                    // Set target
                    xQueueSend(*queue, &target, (TickType_t)2);

                    // Gather data for duration
                    int16_t SG1[duration], SG2[duration];
                    ulong Time[duration];

                    for (uint64_t i = 0; i < duration; i++)
                    {
                        SG1[i] = ads.readADC_SingleEnded(0);
                        Time[i] = xTaskGetTickCount() * (1000 / configTICK_RATE_HZ);
                        SG2[i] = ads.readADC_SingleEnded(1);
                        xTaskDelayUntil(&xLastWakeTime, xPeriod);
                    }

                    // Transfer data
                    Serial.println("TRANSFER START");
                    Serial.println("SG1");
                    for (int16_t sg : SG1)
                    {
                        Serial.println(sg);
                    }
                    Serial.println("SG2");
                    for (int16_t sg : SG2)
                    {
                        Serial.println(sg);
                    }
                    Serial.println("Time");
                    for (ulong t : Time)
                    {
                        Serial.println(t);
                    }
                    Serial.println("TRANSFER OK");
                    led.setPixelColor(0, 0x0000FF00);
                    led.show();
                }
                else if (*(int *)(opmode) == *(int *)("DYNA"))
                {
                    Serial.println("DYNA RECEIVED");
                    // Receive duration uint64_t
                    byte duration_encoded[8];
                    bytesRead = Serial.readBytes(duration_encoded, 8);
                    int16_t duration = byte2int64(duration_encoded); // Decode
                    Serial.println(duration);                        // Echo

                    // Receive encoded control signal int16_t for duration samples
                    byte target_encoded[2 * duration];
                    for (byte b : target_encoded)
                    {
                        bytesRead = Serial.readBytes(&b, 1);
                    }

                    // Decode
                    int16_t target[duration];
                    uint64_t k{0};
                    for (uint64_t i = 0; i < duration; i += sizeof(int16_t))
                    {
                        byte enc[2] = {target_encoded[i], target_encoded[i + 1]};
                        target[k] = byte2int16(enc);

                        Serial.println(target[k]); // Echo

                        k++;
                    }

                    // Gather data for duration while actuating
                    int16_t SG1[duration], SG2[duration];
                    ulong Time[duration];

                    for (uint64_t i = 0; i < duration; i++)
                    {
                        // Set target
                        xQueueSend(*queue, &target, (TickType_t)2);

                        // Get sample
                        SG1[i] = ads.readADC_SingleEnded(0);
                        Time[i] = xTaskGetTickCount() * (1000 / configTICK_RATE_HZ);
                        SG2[i] = ads.readADC_SingleEnded(1);
                        xTaskDelayUntil(&xLastWakeTime, xPeriod);
                    }

                    // Transfer data
                    Serial.println("TRANSFER START");
                    Serial.println("SG1");
                    for (int16_t sg : SG1)
                    {
                        Serial.println(sg);
                    }
                    Serial.println("SG2");
                    for (int16_t sg : SG2)
                    {
                        Serial.println(sg);
                    }
                    Serial.println("Time");
                    for (ulong t : Time)
                    {
                        Serial.println(t);
                    }
                    Serial.println("TRANSFER OK");
                    led.setPixelColor(0, 0x0000FF00);
                    led.show();
                }
                else
                {
                    Serial.println("OP ERR");
                    while (1)
                    {
                        led.setPixelColor(0, 0x00FF0000);
                        led.show();
                        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
                        led.setPixelColor(0, 0x00000000);
                        led.show();
                        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
                    }
                }
            }
            else
            {
                Serial.println("CMD ERR");
                while (1)
                {
                    led.setPixelColor(0, 0x00FF0000);
                    led.show();
                    xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
                    led.setPixelColor(0, 0x00000000);
                    led.show();
                    xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
                }
            }
        }

        xTaskDelayUntil(&xLastWakeTime, xPeriod);
    }
}

#endif // AQUISITION_H