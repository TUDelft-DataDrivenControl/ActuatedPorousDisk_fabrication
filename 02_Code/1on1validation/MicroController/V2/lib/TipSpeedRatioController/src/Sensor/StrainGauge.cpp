#include "StrainGauge.h"
#include <Preferences.h>
#include <Arduino.h>
#include <BasicLinearAlgebra.h>
#include <Adafruit_ADS1X15.h>

#include "../../../../../../../.platformio/packages/framework-arduinoespressif32/libraries/Wire/src/Wire.h"
#include "Calibration/AnalogCalibrationPoint.h"
#include "Interpolation/LeastSquares.h"

Sensor::StrainGauge::StrainGauge(const int positiveDataPin, const int negativeDataPin, const int32_t tareValue) : positiveDataPin(positiveDataPin), negativeDataPin(negativeDataPin), tareValue(tareValue)
{
    pinMode(positiveDataPin, INPUT);
    pinMode(negativeDataPin, INPUT);
}

// /**
//  *DEPRECATED
//  */
void Sensor::StrainGauge::loadCalibrationMap() const
{
    Preferences preferences;
    preferences.begin("StrainGauge", true);
    if (!preferences.isKey("samples"))
    {
        Serial.println("No calibration data found.");
        return;
    }

    Serial.println("Calibration data found, started loading.");

    const size_t byteCount{preferences.getBytesLength("samples")};
    const size_t calibrationPointCount{byteCount / sizeof(Calibration::AnalogCalibrationPoint)};
    const auto calibrationPoints{static_cast<Calibration::AnalogCalibrationPoint *>(malloc(byteCount))};
    preferences.getBytes("samples", calibrationPoints, byteCount);
    preferences.end();

    for (int i = 0; i < calibrationPointCount; i++)
    {
        Serial.print("Calibration calibrated value: ");
        Serial.print(calibrationPoints[i].calibrated);
        Serial.print(" , raw: ");
        Serial.println(calibrationPoints[i].raw);
    }

    this->leastSquares = Interpolation::LeastSquares(calibrationPoints, calibrationPointCount);
    Serial.println("Calibration loaded.");
}

uint16_t Sensor::StrainGauge::readRawData() const
{
    return analogReadMilliVolts(positiveDataPin);
}

float Sensor::StrainGauge::readForce() const
{
    // const long sampleVoltage{analogReadMilliVolts(this->positiveDataPin) - analogReadMilliVolts(this->negativeDataPin)};
    return this->leastSquares.evaluate(analogReadMilliVolts(positiveDataPin)) - tareValue;
}

int32_t Sensor::StrainGauge::readTaredRawData() const
{
    return analogReadMilliVolts(positiveDataPin) - tareValue;
}

/**
 * Constructs a single strain gauge linked to an ADS1115 modules
 * @param channel Channel of the ADS1115 to read for the data
 * @param adsModule Pointer to the active ADS1115 module
 * @param slope Slope of the linear strain-force relationship
 * @param tareValue Value at zero load (if known) which can be set later
 */
Sensor::I2CStrainGauge::I2CStrainGauge(const int channel, Adafruit_ADS1115 *adsModule, const float constantOffset,
                                       const float slope, const long tareValue) : StrainGauge(0, 0, static_cast<short>(tareValue)),
                                                                                  channel(channel), adsModule(adsModule),
                                                                                  constantOffset(-static_cast<float>(tareValue) * slope), slope(slope)
{
}

/**
 * Calculates the force based on the current strain. Is depended on a properly calibrated strain gauge setup.
 * @return force on the strain gauge
 */
float Sensor::I2CStrainGauge::readForce() const
{
    return (constantOffset) + slope * readRawData();
    // return leastSquares.evaluate(adsModule->readADC_SingleEnded(channel) - tareValue);
}

/**
 * Sets the zero load strain of the strain-gauge. Effectively nullifies any preload on the strain-gauges.
 * @param tareValue Value at zero load
 */
void Sensor::StrainGauge::setTare(const int32_t tareValue) const
{
    this->tareValue = tareValue;
}

/**
 * Reads the raw strain without offset correction
 * @return Raw strain in mV
 */
uint16_t Sensor::I2CStrainGauge::readRawData() const
{
    return adsModule->readADC_SingleEnded(channel);
}

/**
 * Reads the raw strain and applies the zero load correction
 * @return Raw strain in mV corrected for zero load offset
 */
int32_t Sensor::I2CStrainGauge::readTaredRawData() const
{
    return adsModule->readADC_SingleEnded(channel) - tareValue;
}
