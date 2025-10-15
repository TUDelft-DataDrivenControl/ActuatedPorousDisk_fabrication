#include "TipSpeedRatioController.h"

#include <SimpleLogger.h>
#include <Actuator/Motor.h>

#include <Sensor/StrainGauge.h>

#include "../../../include/DataPacketContracts.h"

namespace TipSpeedRatioController
{
    /**
     *
     * @param motor Pointer to motor in use
     * @param tipSpeedCurve Tip-speed vs. thrust coefficient curve to set the demand thrust coefficient
     * @param turbineRadius Radius of the turbine in metres
     */
    TipSpeedRatioController::TipSpeedRatioController(const Actuator::Motor *motor,
                                                     const Actuator::TipSpeedCurve *tipSpeedCurve,
                                                     const float turbineRadius) : motorGenerator(motor), tipSpeedCurve(tipSpeedCurve), turbineRadius(turbineRadius),
                                                                                  inverseTurbineRadius(1.f / turbineRadius),
                                                                                  sweptArea(turbineRadius * turbineRadius * static_cast<float>(PI)),
                                                                                  inverseSweptArea(1.f / this->sweptArea)
    {
    }

    /**
     * Sets Enabled state on the controller (when possible).
     */
    bool TipSpeedRatioController::enable() const
    {
        if (this->freestreamVelocity < 0.001f)
        {
            Serial.println(freestreamVelocity);
            return false;
        }
        this->motorGenerator->enable();
        this->motorGenerator->setDirection(Actuator::COUNTER_CLOCKWISE);
        return true;
    }

    void TipSpeedRatioController::disable() const
    {
        this->motorGenerator->disable(true);
    }

    /**
     * Sets the target tip-speed ratio which the TSR controller tries to achieve/maintain.
     * Overwrites any other target set by \ref setTargetThrustCoefficient(float).
     * @param targetRatio Target tip-speed ratio for the TSR controller
     */
    void TipSpeedRatioController::setTargetRatio(const float targetRatio) const
    {
        const float rotationalSpeed{targetRatio * this->freestreamVelocity * this->inverseTurbineRadius * radsToRPM};
        motorGenerator->setTarget(rotationalSpeed);
    }

    /**
     * Sets the excitation function for the thrust coefficient which is used to vary the greedy thrust coefficient.
     * NOTE: due to time constraints the excitation function pointer functionality has been hardcoded instead
     * @param excitationFunctionPtr Pointer to excitation function with selected parameters
     */
    void TipSpeedRatioController::setExcitationFunction(
        float (*excitationFunctionPtr)(unsigned long timeMillis, float freestreamVelocity, float strouhalNumber)) const
    {
        if (!excitationFunctionPtr)
        {
            this->excitationFunctionPtr = &defaultExcitation;
            return;
        }
        this->excitationFunctionPtr = excitationFunctionPtr;
    }

    /**
     * Sets the target thrust coefficient (with excitation) which the TSR controller tries to achieve/maintain.
     * Overwrites any other target set by \ref setTargetRatio(float).
     * NOTE: due to time constraints the excitation function pointer functionality has been hardcoded instead
     * @param targetThrustCoefficient Target thrust coefficient for the TSR controller
     * @param enableExcitation Enables dynamic excitation for the target thrust coefficient. C_t will vary around the targetThrustCoefficient.
     */
    void TipSpeedRatioController::setTargetThrustCoefficient(const float targetThrustCoefficient, const bool enableExcitation) const
    {
        constexpr float maxCt{0.6085f};
        constexpr float minCt{0.4841f};
        constexpr float excitationAmplitude{0.5f * (maxCt - minCt)};
        constexpr float amplitudeFactor{excitationAmplitude /* * yPosition*/};
        constexpr float timeFactor{TWO_PI * (1.f / 1000.f)};

        const float time{timeFactor * static_cast<float>(millis()) * excitationFrequency};

        const float excitation{enableExcitation ? amplitudeFactor * sinf(time) : 0};

        const float targetExcitedThrustCoefficient{targetThrustCoefficient + excitation};

        const float targetRatio{this->tipSpeedCurve->evaluate(targetExcitedThrustCoefficient)};

        setTargetRatio(targetRatio);
    }

    /**
     * Sets the freestream velocity variable for calculations based to the current wind-tunnel velocity
     * @param freestreamVelocity Freestream velocity set in the wind-tunnel
     */
    void TipSpeedRatioController::setFreestreamVelocity(const float freestreamVelocity) const
    {
        this->freestreamVelocity = freestreamVelocity;
        this->inverseFreestreamVelocity = 1.f / this->freestreamVelocity;
        this->dynamicPressureForce = 0.5f * 1.225f * this->freestreamVelocity * this->freestreamVelocity * this->inverseSweptArea;
        this->inverseDynamicPressureForce = 1.f / this->dynamicPressureForce;
    }

    /**
     * Sets the new strouhal number
     * Must not be called without also calling TipSpeedRatioController:setParameters
     * @param strouhalNumber
     */
    void TipSpeedRatioController::setStrouhalNumber(float strouhalNumber) const
    {
        this->strouhalNumber = strouhalNumber;
    }

    /**
     * Sets up all parameters for the measurement run to reduce runtime computation.
     * @param setup pointer to experiment setup for the current measurement run
     */
    void TipSpeedRatioController::setParameters(const ExperimentSetup *setup) const
    {
        setStrouhalNumber(setup->strouhalNumber);
        setFreestreamVelocity(setup->freestreamVelocity);

        constexpr float characteristicLength{3654.f * (0.1f / 126.f)};
        this->excitationFrequency = this->strouhalNumber * this->freestreamVelocity / characteristicLength;
    }

    /**
     * Calculates actual tip speed ratio (estimation) based on specified operating conditions
     * @return Tip speed ratio at current operating conditions
     */
    float TipSpeedRatioController::getActualRatio() const
    {
        return this->motorGenerator->readRotationalSpeed() * this->turbineRadius * this->inverseFreestreamVelocity;
    }
}
