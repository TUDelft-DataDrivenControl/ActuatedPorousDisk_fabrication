// https://esp32s3.com/getting-started.html

#define MAX_EXP_DURATION 15 // s

// Pin defs
#define SCL_PIN 35
#define SDA_PIN 36
#define POT_PIN 1
#define STEP_PIN 4
#define DIR_PIN 2
#define LED_PIN 47

// Modules
#include <Arduino.h>
#include <Wire.h>
#include <queue>

#include <Adafruit_NeoPixel.h>
#include <Adafruit_ADS1X15.h>

// Globals
const unsigned long PERIOD_ACQUISITION{6666}; // us
static unsigned long lastWakeTime{1};
static unsigned long now{1};

Adafruit_NeoPixel led{1, LED_PIN, NEO_RGB + NEO_KHZ800};
Adafruit_ADS1115 ads;

std::queue<int16_t> offset_queu;
int16_t stepper_position{0};
int16_t stepper_target{0};
bool stepper_reached{true};

// Inclusions
#include "StepperCtrl.h"
#include "SerialComm.h"
#include "LedComm.h"

void setup()
{
    // INIT PINS
    pinMode(DIR_PIN, OUTPUT);
    pinMode(STEP_PIN, OUTPUT);
    pinMode(POT_PIN, ANALOG);

    digitalWrite(DIR_PIN, HIGH);
    digitalWrite(DIR_PIN, HIGH);

    // INIT LED
    led.begin();
    led.setBrightness(10);            // 0 to 255 brightest
    led.setPixelColor(0, 0x00FF8000); // Start setup: set orange
    led.show();

    // INIT SERIAL
    Serial.begin(115200);
    while (!Serial)
    {
        blinkError(0x00FF0000); // Serial error: red
    }
    led.setPixelColor(0, 0x00FF8000); // Serial connected: set orange
    led.show();

    // INIT ADS
    while (!ads.begin())
    {
        blinkError(0x000000FF); // ADS error: blue
    }
    led.setPixelColor(0, 0x00FF8000); // ADS connected: set orange
    led.show();

    ads.setGain(GAIN_TWOTHIRDS);
    ads.setDataRate(RATE_ADS1115_860SPS);
}

void loop()
{
    static int64_t duration;
    static int16_t *target = (int16_t *)malloc(sizeof(int16_t) * MAX_EXP_DURATION);
    static int16_t *SG1 = (int16_t *)malloc(sizeof(int16_t) * MAX_EXP_DURATION);
    static int16_t *SG2 = (int16_t *)malloc(sizeof(int16_t) * MAX_EXP_DURATION);
    static ulong *Time = (ulong *)malloc(sizeof(ulong) * MAX_EXP_DURATION);
    static byte *target_encoded = (byte *)malloc(sizeof(byte) * 2 * MAX_EXP_DURATION);

    /////////////////
    // ACQUISITION //
    /////////////////
    char CMD[4];
    receive_cmd(CMD); // Blocking

    if (*(int *)(CMD) == *(int *)("GOTO"))
    {
        do_goto();
    }
    else if (*(int *)(CMD) == *(int *)("STRT"))
    {
        Serial.println("STRT RECEIVED");
        // Receive operation mode
        char opmode[4];
        Serial.readBytes(opmode, 4);

        if (*(int *)(opmode) == *(int *)("STAT"))
        {
            Serial.println("STAT RECEIVED");
            // Receive duration and target
            duration = receive_int64();
            stepper_target = receive_int16();

            // Go to target blockingly
            while (step_stepper())
            {
                ;
            }

            // Gather data for duration
            uint64_t idx4 = 0;
            led.setPixelColor(0, 0x0000FF); // Start exp: set blue
            led.show();
            while (idx4 < duration)
            {
                now = micros();
                if (now - lastWakeTime > PERIOD_ACQUISITION)
                {
                    SG1[idx4] = ads.readADC_SingleEnded(0);
                    Time[idx4] = now;
                    SG2[idx4] = ads.readADC_SingleEnded(1);

                    lastWakeTime = now;
                    idx4++;
                }
            }
            led.setPixelColor(0, 0xf5ef42); // Start transmit: set yellow
            led.show();
            transmit_data(SG1, SG2, Time, duration);
        }
        else if (*(int *)(opmode) == *(int *)("DYNA"))
        {
            Serial.println("DYNA RECEIVED");
            // Receive duration
            duration = receive_int64();

            // Receive encoded control signal int16_t for duration samples
            uint64_t idx1 = 0;
            while (idx1 < 2 * duration)
            {
                idx1 += (uint64_t)(Serial.readBytes(&target_encoded[idx1], 1)); // Read
            }

            uint64_t idx2{0};
            for (uint64_t i = 0; i < 2 * duration; i += 2)
            {
                byte enc[2] = {target_encoded[i], target_encoded[i + 1]}; // Decode
                target[idx2] = byte2int16(enc);                           // Store
                Serial.println(target[idx2]);                             // Echo
                idx2++;
            }
            // Gather data for duration while actuating
            uint64_t idx3 = 0;
            led.setPixelColor(0, 0x0000FF); // Start exp: set blue
            led.show();
            while (idx3 < duration)
            {
                now = micros();
                if (now - lastWakeTime > PERIOD_ACQUISITION)
                {
                    SG1[idx3] = ads.readADC_SingleEnded(0);
                    Time[idx3] = now;
                    SG2[idx3] = ads.readADC_SingleEnded(1);

                    lastWakeTime = now;
                    idx3++;
                }
                step_stepper();
            }
            led.setPixelColor(0, 0xf5ef42); // Start transmit: set yellow
            led.show();
            transmit_data(SG1, SG2, Time, duration);
        }
        else
        {
            Serial.println("OP ERR");
            while (1)
            {
                blinkError(0x00FF00FF); // purple
            }
        }
    }
    else
    {
        Serial.println("CMD ERR");
        while (1)
        {
            blinkError(0x00FFFFFF); // white
        }
    }
}
