#ifndef MOTOR_H
#define MOTOR_H

#include "MotorProperties.h"

namespace Actuator
{
    enum Direction
    {
        CLOCKWISE = false,
        COUNTER_CLOCKWISE = true,
    };

    /**
     * A class to interface with the ESCON 32/6 DC servo controller running a single motor.
     */
    class Motor
    {
    private:
        const MotorData* data;
        const int enablePin;
        const int stopPin;
        const int directionPin;
        const int targetSetPin;
        const float maxSetPoint;
        const float minSetPoint;
        mutable Direction direction{COUNTER_CLOCKWISE};
        mutable bool outputEnabled{false};
        mutable bool enabled{false};
        int mapValue(float value) const;

    public:
        Motor(const MotorData* data, int enablePin, int stopPin, int directionPin,
              int targetSetPin, float minSetPoint,
              float maxSetPoint);
        void enable() const;
        void disable(bool stop) const;
        void stop() const;
        void run() const;
        Direction getDirection() const { return this->direction; }
        void setTarget(float target) const;
        void setTarget(float target, Direction direction) const;
        void switchDirection() const;
        void setDirection(Direction direction) const;
        void enableOutput() const;
        void disableOutput() const;
        float readRotationalSpeed() const;
        float readCurrent() const;
        bool isEnabled() const;
    };
}

#endif // MOTOR_H
