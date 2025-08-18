#ifndef STRAIN_GAUGE_H
#define STRAIN_GAUGE_H

#include <Adafruit_ADS1X15.h>
#include <BasicLinearAlgebra.h>
#include "Interpolation/LeastSquares.h"

namespace Sensor
{
    /**
     * ABSTRACT CLASS, DO NOT INSTANTIATE
     */
    class StrainGauge
    {
    private :
        const int positiveDataPin;
        const int negativeDataPin;
    protected:
        mutable int32_t tareValue;
        mutable Interpolation::LeastSquares leastSquares{};
    public:
        virtual ~StrainGauge() = default;
        explicit StrainGauge(int positiveDataPin, int negativeDataPin, int32_t tareValue);
        void loadCalibrationMap() const;
        void tare() const;
        void setTare(int32_t tareValue) const;
        virtual uint16_t readRawData() const;
        virtual float readForce() const;
        virtual int32_t readTaredRawData() const;
    };

    /**
     * Strain-gauge class for use with an ADS1115 I2C ADC
     */
    class I2CStrainGauge final : public StrainGauge
    {
    private:
        const int channel;
        Adafruit_ADS1115* adsModule;
        const float constantOffset;
        const float slope;

    public:
        I2CStrainGauge(int channel, Adafruit_ADS1115* adsModule, float constantOffset, float slope, long tareValue);
        float readForce() const override;
        uint16_t readRawData() const override;
        int32_t readTaredRawData() const override;
    };
}

#endif //STRAIN_GAUGE_H
