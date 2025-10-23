#ifndef SETUP_H
#define SETUP_H

#include <Arduino.h>
#include <Wire.h>

#include <Adafruit_NeoPixel.h>
#include <Adafruit_ADS1X15.h>

#define SCL_PIN 35
#define SDA_PIN 36
#define POT_PIN 2
#define STEP_PIN 43
#define DIR_PIN 12
#define LED_PIN 47

// RTOS setup
TaskHandle_t blinkLedHandle;
TaskHandle_t actuationHandle;
TaskHandle_t acquisitionHandle;

#endif // SETUP_H
