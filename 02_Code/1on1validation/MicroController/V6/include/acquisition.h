#ifndef AQUISITION_H
#define AQUISITION_H

#include <queue>

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

inline int16_t step_towards(int16_t tar, int16_t pos)
{
    // For timing see section 7.6 of drv8825 docs
    // https://www.ti.com/lit/ds/symlink/drv8825.pdf
    int16_t dir{0};
    if (tar > pos)
    {
        dir = 1;
        digitalWrite(DIR_PIN, LOW);
        delayMicroseconds(5); // Setup time
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(40); // Pulse time
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(100); // Pulse time
    }
    else if (tar < pos)
    {
        dir = -1;
        digitalWrite(DIR_PIN, HIGH);
        delayMicroseconds(5); // Setup time
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(40); // Pulse time
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(100); // Pulse time
    }
    return dir;
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

    // INIT ADC
    // https://how2electronics.com/how-to-use-ads1115-16-bit-adc-module-with-esp32/
    Adafruit_ADS1115 ads;
    while (!ads.begin())
    {
        led.setPixelColor(0, 0x00FF00FF);
        led.show();
        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
        led.setPixelColor(0, 0x00000000);
        led.show();
        xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 500);
    }
    ads.setGain(GAIN_SIXTEEN);
    ads.setDataRate(RATE_ADS1115_860SPS);

    // INIT STEPPER
    int16_t target_storage{0};
    int16_t position{0};

    std::queue<int16_t> offset_queu;
    std::queue<int16_t> offset;

    // BOOT OK
    Serial.println("BOOT OK");
    led.setPixelColor(0, 0x0000FF00);
    led.show();

    // MAIN LOOP
    for (;;)
    {
        // Wait for 4 bytes of CMD
        if (Serial.available() >= 4)
        {
            vTaskDelay(200 * portTICK_PERIOD_MS); // give background tasks some CPU time before acquisition
            led.setPixelColor(0, 0x00000000);     // cmd received, set off
            led.show();

            // Receive CMD
            char CMD[4];
            Serial.readBytes(CMD, 4);

            const byte GOTO[4]{'G', 'O', 'T', 'O'};
            const byte STRT[4]{'S', 'T', 'R', 'T'};

            if (memcmp(CMD, GOTO, 4) == 0)
            {
                delay(10);
                Serial.println("GOTO RECEIVED");
                // Receive target int16_t
                byte target_encoded[2];
                Serial.readBytes(target_encoded, 2);
                // Decode target
                int16_t target = byte2int16(target_encoded);
                // Echo target
                Serial.println(target);

                // Go to target blockingly
                while (position - offset.back() != target)
                {
                    position += step_towards(target, position - offset.back());
                    xTaskDelayUntil(&xLastWakeTime, portTICK_PERIOD_MS * 10);
                }
                target_storage = target;
                Serial.println("GOTO COMPLETE");
            }
            else if (memcmp(CMD, STRT, 4) == 0)
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
                    if (i % 2000)                           // Every 2000 elements, yield to background processes :(
                    {
                        vTaskDelay(1);
                    }
                }

                // Gather data for duration while actuating
                int16_t SG1[duration], SG2[duration];
                ulong Time[duration];

                led.setPixelColor(0, 0x000000FF); // start sampling, set blue
                led.show();
                xLastWakeTime = xTaskGetTickCount();
                for (uint64_t i = 0; i < duration; i++)
                {
                    // Get sample
                    SG1[i] = ads.readADC_SingleEnded(0);
                    Time[i] = xTaskGetTickCount() * (1000 / configTICK_RATE_HZ);
                    SG2[i] = ads.readADC_SingleEnded(1);

                    // Run motor until time runs out
                    while (position - offset.back() != target[i]) // && xTaskGetTickCount() - xLastWakeTime < xPeriod - (TickType_t)(1))
                    {
                        position += step_towards(target[i], position - offset.back());
                    }

                    xTaskDelayUntil(&xLastWakeTime, xPeriod);
                }
                target_storage = target[duration - 1];

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

        // HOME STEPPER
        int16_t potread = (int16_t)(map(analogRead(POT_PIN), (4096 / 2), (4096 / 1), -213, 213));
        offset_queu.push(potread);
        while (offset_queu.size() > 25)
        {
            offset_queu.pop();
        }

        offset = offset_queu;
        while (offset.size() > 1)
        {
            offset.back() += offset.front();
            offset.pop();
        }
        offset.back() /= (int16_t)(offset_queu.size());

        position += step_towards(target_storage, position - offset.back());

        xTaskDelayUntil(&xLastWakeTime, xPeriod);
    }
}

#endif // AQUISITION_H