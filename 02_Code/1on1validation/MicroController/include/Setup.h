#ifndef SETUP_H
#define SETUP_H

#include <Wire.h>
#include <Adafruit_NeoPixel.h>

#include "TipSpeedRatioController.h"
#include "Actuator/Motor.h"
#include "Sensor/StrainGauge.h"
#include "PorousDisk.h"
#include "ExperimentSetup.h"

uint32_t blinkColour{0x00FF0000};
constexpr int ledPin{47};
Adafruit_NeoPixel led{1, ledPin, NEO_RGB + NEO_KHZ800};
inline void setBlinkColour(uint32_t colour);
inline void blinkError();

constexpr int motorTargetSetPin{34};
constexpr int motorStopPin{38};
constexpr int motorEnablePin{37};
constexpr int motorDirectionPin{33};
constexpr int motorMinSpeed{0};
constexpr int motorMaxSpeed{10000};

constexpr int stepperStepPin{2};
constexpr int stepperDirPin{4};
constexpr int potmeterPin{1};

constexpr float xPosition{0.45f};
constexpr float yPosition{-0.45f};
constexpr int settlingTimeMillis{1000 * 15};
constexpr int tareSampleCount{600};

ExperimentSetup experimentSetup;
static Adafruit_ADS1115 adsModule{};
static AccelStepper stepper(AccelStepper::DRIVER, stepperStepPin, stepperDirPin);
static const PorousDisk porousDisk(xPosition, yPosition, potmeterPin, &stepper);
static const Sensor::I2CStrainGauge upstreamStrainGauge{0, &adsModule, 0, 1, 0};
static const Sensor::I2CStrainGauge downstreamStrainGauge{1, &adsModule, 0, 1, 0};
static const Sensor::I2CStrainGauge noiseStrainGauge{2, &adsModule, 0, 1, 0};
static const Actuator::MotorData motorData{3.52f, 2710.0f, 2240.0f, 0.6480f, 4.5f};
static const Actuator::Motor motor{
    &motorData, motorEnablePin, motorStopPin, motorDirectionPin, motorTargetSetPin, motorMinSpeed, motorMaxSpeed};
// Full range of TSR controller
// static const Actuator::TipSpeedCurve tsrCurve{
//     -55.86432561f, 367.0112003f, -851.26188635f, 849.65730629f, -301.88309099f
// };

// Localised fit to 1.2-3.0 giving more accurate operating conditions for Ct
// static const Actuator::TipSpeedCurve tsrCurve{
//     -1038.70806104f, 7437.40485608f, -19852.28798888f, 23427.97317105f, -10301.93183861f
// };

// Localised fit to 1.2-2.4 giving more accurate operating conditions for Ct and less powers
static const Actuator::TipSpeedCurve tsrCurve{-164.4619962f, 933.33020578f, -1753.98595613f, 1102.40144751f};

static const TipSpeedRatioController::TipSpeedRatioController tsrController{&motor, &tsrCurve, 0.05f};

/**
 * Configures all pins and onboard parameters correctly. Must be called before operation!
 */
inline void setupPorts()
{
    analogReadResolution(12);
    analogWriteResolution(12);
    analogWriteFrequency(2000); // Play around with the value, but note the update rate of the tasks is a 1000Hz at most, so don´t go too low
    pinMode(potmeterPin, INPUT);
    pinMode(motorEnablePin, OUTPUT);
    pinMode(motorStopPin, OUTPUT);
    pinMode(motorDirectionPin, OUTPUT);
    pinMode(motorTargetSetPin, OUTPUT);
    pinMode(stepperStepPin, OUTPUT);
    pinMode(stepperDirPin, OUTPUT);

    led.begin();

    led.setPixelColor(0, 0, 0, 0);
    led.show();
}

/**
 * Configures the necessary communication protocols needed for the controller. Must be called before operation!
 */
inline void setupCommunication()
{
    Serial.begin(115200);

    adsModule.setGain(GAIN_ONE);
    adsModule.setDataRate(RATE_ADS1115_860SPS);

    if (!adsModule.begin(0x48))
    {
        blinkError();
    }

    Wire.setClock(400000);
}

/**
 * Sets blink colour for the rgb LED.
 * @param colour 0x00RRGGBB
 */
inline void setBlinkColour(const uint32_t colour)
{
    blinkColour = colour;
}

/**
 * Blocking function blinking the LED red and blocking further active task execution
 */
[[noreturn]] inline void blinkError()
{
    for (;;)
    {
        setBlinkColour(0x00FF0000);
    }
}

#endif // SETUP_H
