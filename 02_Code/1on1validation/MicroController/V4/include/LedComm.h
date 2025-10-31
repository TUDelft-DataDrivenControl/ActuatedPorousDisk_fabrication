#ifndef LED_COMM_H
#define LED_COMM_H

void blinkError(uint32_t colour)
{
    led.setPixelColor(0, colour);
    led.show();
    delay(500);
    led.setPixelColor(0, colour);
    led.show();
    delay(500);
}

#endif // LED_COMM_H