
#define PERIOD_ACQUISITION 8 // ms

// https://esp32s3.com/getting-started.html

// Pin defs
#define SCL_PIN 35
#define SDA_PIN 36
#define POT_PIN 1
#define STEP_PIN 4
#define DIR_PIN 2
#define LED_PIN 47

// Modules
#include <Adafruit_NeoPixel.h>
#include <Adafruit_ADS1X15.h>

#include "acquisition.h"

// RTOS setup
TaskHandle_t acquisitionHandle;

void setup()
{
    // INIT PINS
    pinMode(DIR_PIN, OUTPUT);
    pinMode(STEP_PIN, OUTPUT);
    pinMode(POT_PIN, ANALOG);

    digitalWrite(DIR_PIN, HIGH);
    digitalWrite(DIR_PIN, HIGH);

    // INIT RTOS TASKS

    // https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/freertos_additions.html#_CPPv423xTaskCreatePinnedToCore14TaskFunction_tPCKcK8uint32_tPCv11UBaseType_tPC12TaskHandle_tK10BaseType_t
    // https://freertos.org/Documentation/02-Kernel/04-API-references/02-Task-control/03-xTaskDelayUntil
    xTaskCreate(&acquisitionTask, "acquisitionTask", 262144, NULL, 6, &acquisitionHandle);
}

TickType_t xLastWakeTimeLoop = xTaskGetTickCount();
void loop()
{
    xTaskDelayUntil(&xLastWakeTimeLoop, portTICK_PERIOD_MS * 1000 * 60);
}