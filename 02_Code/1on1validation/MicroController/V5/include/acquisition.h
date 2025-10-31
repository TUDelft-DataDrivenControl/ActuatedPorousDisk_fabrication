#ifndef AQUISITION_H
#define AQUISITION_H

// https://how2electronics.com/how-to-use-ads1115-16-bit-adc-module-with-esp32/

// Decoding
inline int16_t byte2int16(byte enc[2])
{
    return (((int16_t)(((uint8_t *)(enc))[0]) << 0) +
            ((int16_t)(((uint8_t *)(enc))[1]) << 8));
}

inline uint64_t byte2uint64(byte enc[8])
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
    TickType_t xPeriod = portTICK_PERIOD_MS * PERIOD_ACQUISITION;

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
            led.setPixelColor(0, 0x00000000); // cmd received, set off
            led.show();

            // Receive CMD
            char CMD[4];
            Serial.readBytes(CMD, 4);

            if (*(int *)(CMD) == *(int *)("GOTO"))
            {
                Serial.println("GOTO RECEIVED");
                // Receive target int16_t
                byte target_encoded[2];
                Serial.readBytes(target_encoded, 2);
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
                byte duration_encoded[8];
                Serial.readBytes(duration_encoded, 8);
                uint64_t duration = byte2uint64(duration_encoded); // Decode
                Serial.println(duration);                          // Echo

                // Receive encoded control signal int16_t for duration samples
                byte target_encoded[2];
                int16_t target[duration];
                for (uint64_t i = 0; i < duration; i++)
                {
                    Serial.readBytes(target_encoded, 2);    // Read
                    target[i] = byte2int16(target_encoded); // Decode
                    Serial.println(target[i]);              // Echo
                }

                // Gather data for duration while actuating
                int16_t SG1[duration], SG2[duration];
                ulong Time[duration];

                led.setPixelColor(0, 0x000000FF); // start sampling, set blue
                led.show();
                xLastWakeTime = xTaskGetTickCount();
                for (uint64_t i = 0; i < duration; i++)
                {
                    // Set target
                    xQueueSend(*queue, &target[i], (TickType_t)2);

                    // Get sample
                    SG1[i] = ads.readADC_SingleEnded(0);
                    Time[i] = xTaskGetTickCount() * (1000 / configTICK_RATE_HZ);
                    SG2[i] = ads.readADC_SingleEnded(1);
                    xTaskDelayUntil(&xLastWakeTime, xPeriod);
                }

                led.setPixelColor(0, 0x00888888); // start transfer, set gray
                led.show();
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

        led.setPixelColor(0, 0x0000FF00); // Ready for cmd, set green
        led.show();
        xTaskDelayUntil(&xLastWakeTime, xPeriod);
    }
}

#endif // AQUISITION_H