#ifndef BLINK_LED_H
#define BLINK_LED_H

///////////////////
/**  REFERENCES  */
///////////////////
// https://adafruit.github.io/Adafruit_NeoPixel/html/class_adafruit___neo_pixel.html#a19fc274330c0e65907929ee03b93b1c3
// https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf

///////////////////
/** DECLARATIONS */
///////////////////
uint32_t blinkColour{0xFF000000};

Adafruit_NeoPixel led{1, LED_PIN, NEO_RGB + NEO_KHZ800};

void blinkLedTask(void *parameter);

///////////////////
/** DEFINITIONS  */
///////////////////

[[noreturn]] void blinkLedTask(void *parameter)
{
    QueueHandle_t *queue{static_cast<QueueHandle_t *>(parameter)};

    TickType_t xLastWakeTime = xTaskGetTickCount();
    TickType_t xPeriod = portTICK_PERIOD_MS * round(1000 / FREQ_LED);
    for (;;)
    {
        uint32_t colour;
        xQueueReceive(*queue, &(colour), (TickType_t)4);
        // colour : --RRGGBB
        led.setPixelColor(0, colour);
        led.show();

        xTaskDelayUntil(&xLastWakeTime, xPeriod);
    }
}
#endif // BLINK_LED_H