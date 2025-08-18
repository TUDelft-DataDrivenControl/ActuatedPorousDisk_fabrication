#ifndef EXPERIMENT_SETUP_H
#define EXPERIMENT_SETUP_H

enum ThrustMode
{
    STATIC = 0,
    DYNAMIC = 1
};

enum TurbineSetup
{
    POROUS_DISC = 0,
    MINI_TURBINE = 1
};

/**
 * All test setup parameters stored in a single structure for compact transfer between host and controller
 */
struct __attribute__((packed)) ExperimentSetup
{
    const float strouhalNumber;
    const float freestreamVelocity;
    const TurbineSetup turbineSetup;
    const ThrustMode thrustMode;
    const int measurementTime;
    /**
     * Should the strain-gauges be zeroed before measurement? In general this is best to do each run.
     */
    const bool tare;

    ExperimentSetup() : strouhalNumber(0.1f), freestreamVelocity(5.f), turbineSetup(POROUS_DISC), thrustMode(STATIC),
                        measurementTime(60), tare(false)
    {
    }

    ExperimentSetup(const float strouhalNumber, const float freestreamVelocity, const TurbineSetup turbineSetup,
                    const ThrustMode thrustMode, const int measurementTime, const bool tare) :
        strouhalNumber(strouhalNumber), freestreamVelocity(freestreamVelocity), turbineSetup(turbineSetup),
        thrustMode(thrustMode), measurementTime(measurementTime), tare(tare)
    {
    }
};

#endif //EXPERIMENT_SETUP_H
