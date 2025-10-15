#ifndef POROUSDISK_H
#define POROUSDISK_H

#include <AccelStepper.h>

class PorousDisk // Controller class for a single PD
{
private:
    mutable AccelStepper *stepper; // Stepper motor class
    const int potPin;

    // Wind (farm) related variables
    static constexpr float Lx_wf  {0.9}; // [m] Wind farm length
    static constexpr float Ly_wf {0.9}; // [m] Wind farm width
    static constexpr float Uinf  {9};    // [m/s] Free stream speed
    mutable float strouhalNumber;             // [-] Strouhal number

    /**
     * Turbine X position in wind farm
     */
    const float xPos;
    /**
     * Turbine Y position in wind farm
     */
    const float yPos;

    // Disk and motor variables
    static constexpr long microStepping{32}; // microstepping multiplier
    static constexpr long stepsPerRevolution{400*microStepping};
    static constexpr float angMin{0.f}; // [rad] Minimum angle
    static constexpr float angMax{2.f * PI / 180.0f}; // [rad] Maximum angle
    static constexpr float angStep{0.9f * PI / 180.0f / microStepping}; // [rad] Step angle
    static constexpr float maxSpeed{2.6180f / angStep}; // [steps/s] Maximum motor speed
    static constexpr float acceleration{3200000.0f}; // [steps/s/s] Motor acceleration
    static constexpr int minPulseWidth{3}; // [ms] Minimum pulse width allowed by the stepper driver

    static constexpr float Ct_1{2.0 / Ly_wf}; // Precalculations for actuation function
    static constexpr float Ct_2{TWO_PI * Uinf / Ly_wf};
    static constexpr float Ct_3{0.7 * Ly_wf};

    float actuationFunc(float) const;           // Actuation function of time and position
    int potPos {analogRead(potPin)}; // Datum potmeter position

    constexpr static float mapFloat(const float x, const float in_min, const float in_max, const float out_min, const float out_max)
    {
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
    }

public:
    PorousDisk(float X, float Y, int potPin, AccelStepper* stepper);
    void operatePD(float) const;
    void zeroPD(void* params) const;
    void homePD(void* params) const;
    void setStrouhalNumber(float strouhalNumber) const;
    void setToAngleRadians(float newAngle) const;
    void setToAngleDegrees(float newAngle) const;
    void setHome() const;

    // Debugging
    void printStepperPos();
};

#endif // POROUSDISK_H