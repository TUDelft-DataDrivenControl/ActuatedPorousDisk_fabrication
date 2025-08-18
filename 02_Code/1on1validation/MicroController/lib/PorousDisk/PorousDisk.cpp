#include "PorousDisk.h"

PorousDisk::PorousDisk(const float X, const float Y, const int potPin, AccelStepper* stepper) : stepper(stepper),
    potPin(potPin), xPos(X), yPos(Y)
{
    stepper->setMaxSpeed(maxSpeed);
    stepper->setAcceleration(acceleration);
    stepper->setMinPulseWidth(minPulseWidth);
    stepper->setCurrentPosition(0);
}

void PorousDisk::operatePD(const float t) const
{
    const float Ct{actuationFunc(t)};
    const float ang{mapFloat(Ct, -1.0, 1.0, angMin, angMax)};
    stepper->moveTo(ang / angStep);
    for (int i = 0; i <= 20; i++)
    {
        stepper->run();
        if (stepper->distanceToGo() == 0)
        {
            break;
        }
    }
}

float PorousDisk::actuationFunc(const float t) const
{
    return Ct_1 * yPos * sin(
        Ct_2 * strouhalNumber * t - (fmod(xPos, Ct_3 / strouhalNumber)) / Ct_3 * strouhalNumber * TWO_PI);
}

void PorousDisk::zeroPD(void* params) const
{
    //TODO: What is potPos?
    const float target{mapFloat(analogRead(this->potPin) - potPos, 0.0, 4095.0, 6.f * angMin, angMax * 6.f)};
    stepper->runToNewPosition((target / angStep));
}

void PorousDisk::setHome() const
{
    stepper->setCurrentPosition(0);
}

void PorousDisk::homePD(void* params) const
{
    stepper->runToNewPosition(0);
}

void PorousDisk::setStrouhalNumber(const float strouhalNumber) const
{
    this->strouhalNumber = strouhalNumber;
}

/**
 * Sets the PD angle in absolute terms
 * @param newAngle new angle in radians
 */
void PorousDisk::setToAngleRadians(const float newAngle) const
{
    stepper->moveTo(static_cast<long>(newAngle / angStep));
    stepper->runToPosition();
}

void PorousDisk::setToAngleDegrees(const float newAngle) const
{
    stepper->moveTo(static_cast<long>((newAngle * DEG_TO_RAD) / angStep));
    stepper->runToPosition();
}

void PorousDisk::printStepperPos()
{
    Serial.print(angMin / angStep); // To freeze the lower limit
    Serial.print(" ");
    Serial.print(angMax / angStep); // To freeze the upper limit
    Serial.print(" ");
    Serial.print(stepper->currentPosition());
    Serial.print(" ");
    Serial.println(stepper->targetPosition());
}
