#ifndef TIP_SPEED_RATIO_CONTROLLER_H
#define TIP_SPEED_RATIO_CONTROLLER_H

#include "../../../include/ExperimentSetup.h"
#include "Actuator/Motor.h"
#include "Sensor/StrainGauge.h"
#include "Actuator/TipSpeedCurve.h"

//TODO: SIMD optimisation for wind farms
//For expression parsing https://github.com/beltoforion/muparser

namespace TipSpeedRatioController
{
    /**
     * A class for a tip-speed ratio controller interfacing with a motor controller
     */
    class TipSpeedRatioController
    {
    private:
        const Actuator::Motor *motorGenerator;
        const Actuator::TipSpeedCurve *tipSpeedCurve;
        const float turbineRadius;
        const float inverseTurbineRadius;
        const float sweptArea;
        const float inverseSweptArea;
        static constexpr float radsToRPM{30.f / static_cast<float>(PI)};
        mutable float (*excitationFunctionPtr)(unsigned long timeMillis, float freestreamVelocity, float strouhalNumber){&defaultExcitation};
        mutable float freestreamVelocity{0.f};
        mutable float inverseFreestreamVelocity{0.f};
        mutable float dynamicPressureForce{0.f};
        mutable float inverseDynamicPressureForce{0.f};
        mutable float strouhalNumber{0.f};
        mutable float excitationFrequency{0.f};
        static float defaultExcitation(const unsigned long timeMillis, const float freestreamVelocity, const float strouhalNumber) { return 0.0f; }
        void setFreestreamVelocity(float freestreamVelocity) const;
        void setStrouhalNumber(float strouhalNumber) const;

    public:
        TipSpeedRatioController(const Actuator::Motor *motor, const Actuator::TipSpeedCurve *tipSpeedCurve, float turbineRadius);
        bool enable() const;
        void disable() const;
        void setTargetRatio(float targetRatio) const;
        void setExcitationFunction(float (*excitationFunctionPtr)(unsigned long timeMillis, float freestreamVelocity, float strouhalNumber)) const;
        void setTargetThrustCoefficient(float targetThrustCoefficient, bool enableExcitation) const;
        void setParameters(const ExperimentSetup *setup) const;
        float getActualRatio() const;
    };
}

#endif // TIP_SPEED_RATIO_CONTROLLER_H
