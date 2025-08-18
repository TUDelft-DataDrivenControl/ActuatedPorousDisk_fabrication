#include "Motor.h"
#include <Arduino.h>

namespace Actuator
{
    /**
     * @param data Motor data containing physical parameters
     * @param enablePin Pin to enable motor controller - HIGH -> enables
     * @param stopPin Pin to stop motor from running - HIGH -> stops
     * @param directionPin Pin to set direction - HIGH -> CCW
     * @param targetSetPin Pin to set target speed with PWM
     * @param minSetPoint Minimum absolute setpoint of the motor's rotational speed
     * @param maxSetPoint Maximum absolute setpoint of the motor's rotational speed
     */
    Motor::Motor(const MotorData *data, const int enablePin, const int stopPin,
                 const int directionPin, const int targetSetPin, const float minSetPoint, const float maxSetPoint) :
        data(data), enablePin(enablePin), stopPin(stopPin), directionPin(directionPin),
        targetSetPin(targetSetPin), maxSetPoint(maxSetPoint), minSetPoint(minSetPoint)
    {
        pinMode(enablePin, OUTPUT);
        pinMode(stopPin, OUTPUT);
        pinMode(directionPin, OUTPUT);
        pinMode(targetSetPin, OUTPUT);

        this->setTarget(minSetPoint);
    }

    /**
     * Enables motor. Motor will not be set to zero set-point upon enabling!
     */
    void Motor::enable() const
    {
        this->enabled = true;
        analogWrite(this->enablePin, 4095);
        setDirection(this->direction);
    }

    /**
     * Disables motor. Includes stop functionality.
     * @param stop Stop the motor as opposed to letting it spin freely
     */
    void Motor::disable(const bool stop) const
    {
        this->enabled = false;
        analogWrite(this->enablePin, 0);
        if (stop)
            this->stop();
    }

    /**
     * Stops the motor to zero speed without disabling it.
     */
    void Motor::stop() const
    {
        analogWrite(this->stopPin, 4095);
    }

    /**
     * Starts running the motor when stopped
     */
    void Motor::run() const
    {
        if(!this->enabled)
            return;
        analogWrite(this->stopPin, 0);
    }

    /**
     * Maps any value to the respective analog value within the maximum and minimum set-points specified upon construction.
     * @param value Target set-point, actual physical value.
     * @return Analog value within range of analog resolution of ADC.
     */
    int Motor::mapValue(const float value) const
    {
        if (value < this->minSetPoint) return 511;
        if (value > this->maxSetPoint) return 3583;

        constexpr int analogResolution{3073};
        constexpr int bias{511};
        return static_cast<int>(round(
            bias + analogResolution * (value - this->minSetPoint) / (this->maxSetPoint - this->minSetPoint)));
    }

    /**
     * Sets the output to the specified value (clamped within minimum and maximum).
     * @param target Physical value of target set-point.
     */
    void Motor::setTarget(const float target) const
    {
        analogWrite(this->targetSetPin, this->mapValue(target));
    }

    /**
     * Sets the output to the specified value (clamped within minimum and maximum) and sets direction.
     * @param target Physical value of target set-point
     * @param direction Direction of the motor
     */
    void Motor::setTarget(const float target, const Direction direction) const
    {
        setTarget(target);
        setDirection(direction);
    }

    /**
     * Switches direction of set-point. For speed control this will switch rotational direction.
     * For current control this will switch from generator to driver mode?
     */
    void Motor::switchDirection() const
    {
        this->setDirection(static_cast<Direction>(!this->direction));
    }

    /**
     * Sets a specific direction for the motor
     * @param direction Direction of the motor
     */
    void Motor::setDirection(const Direction direction) const
    {
        this->direction = direction;
        analogWrite(this->directionPin, this->direction*4095);
    }

    /**
     * [NOT IMPLEMENTED] Enables the motor data logging functionality
     */
    void Motor::enableOutput() const
    {
        this->outputEnabled = true;
    }

    /**
     * [NOT IMPLEMENTED] Disables the motor data logging functionality
     */    void Motor::disableOutput() const
    {
        this->outputEnabled = false;
    }

    /**
     * [NOT IMPLEMENTED] Reads the rotational speed from the controller
     */
    float Motor::readRotationalSpeed() const
    {
        return 0.f;
    }

    /**
     * [NOT IMPLEMENTED] Reads the current from the controller
     */
    float Motor::readCurrent() const
    {
        return 0.f;
    }

    bool Motor::isEnabled() const
    {
        return this->enabled;
    }
}
