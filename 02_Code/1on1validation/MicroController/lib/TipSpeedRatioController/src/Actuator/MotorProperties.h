#ifndef MOTOR_PROPERTIES_H
#define MOTOR_PROPERTIES_H

namespace Actuator
{
  /**
   * A struct to describe physical properties of the motor useful for calculations, control etc.
   */
  struct MotorData
  {
    const float torqueConstant;
    const float speedConstant;
    const float speedTorqueGradient;
    const float maxCurrent;
    const float maxVoltage;

    MotorData(const float torqueConstant, const float speedConstant, const float speedTorqueGradient, const float maxCurrent,
                    const float maxVoltage) :
      torqueConstant(torqueConstant), speedConstant(speedConstant), speedTorqueGradient(speedTorqueGradient), maxCurrent(maxCurrent), maxVoltage(maxVoltage)
    {
    }
  };
}

#endif //MOTOR_PROPERTIES_H
