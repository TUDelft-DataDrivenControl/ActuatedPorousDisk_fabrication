#ifndef EXCITATION_FUNCTION_H
#define EXCITATION_FUNCTION_H

#include <Arduino.h>
#include <Setup.h>

constexpr float propagationFactor{0.7f};
constexpr float maxCt {0.6085f};
constexpr float minCt {0.4841f};
constexpr float excitationAmplitude{0.5f * (maxCt - minCt)};
constexpr float amplitudeFactor{excitationAmplitude /* * yPosition*/ };
constexpr float timeFactor{TWO_PI* (1.f/1000.f)};

/**
 * Excitation function for the miniature turbine. Outputs the excitation of the thrust coefficient without constant offset.
 * @param timeMillis current time in control loop
 * @param freestreamVelocity freestream velocity of the wind tunnel
 * @param excitationFrequency frequency of the excitation function
 * @return Excitation of the thrust coefficient without constant offset
 */
inline float excitation(const unsigned long timeMillis, const float freestreamVelocity, const float  excitationFrequency)
{
    const float time{timeFactor * static_cast<float>(timeMillis) * excitationFrequency};

    return amplitudeFactor * sinf(time);
}

#endif //EXCITATION_FUNCTION_H
