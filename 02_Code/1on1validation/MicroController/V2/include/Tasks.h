#ifndef TASKS_H
#define TASKS_H

#include "Setup.h"
#include "SimpleLogger.h"
#include "DataPacketContracts.h"
#include "SerialCommand.h"
#include "ExcitationFunction.h"

TaskHandle_t startExperimentHandle{nullptr};
TaskHandle_t commandDecodeHandle{nullptr};
TaskHandle_t runControlLoopHandle{nullptr};
TaskHandle_t runStepperHandle{nullptr};
TaskHandle_t tareStrainGaugesHandle{nullptr};
TaskHandle_t runSamplingHandle{nullptr};
TaskHandle_t blinkLedHandle;

void startExperimentTask(void *pvParameters);

/**
 * Blinks the LED at a steady 1000ms rate
 * @param pvParaneters pointer to uint32_t of the blink colour
 */
[[noreturn]] inline void blinkLedTask(void *pvParaneters)
{
    const uint32_t *colour{static_cast<uint32_t *>(pvParaneters)};

    for (;;)
    {
#ifndef HAS_LED
        led.setPixelColor(0, *colour);
        led.show();
        vTaskDelay(500);
        led.setPixelColor(0, 0);
        led.show();
#endif
        vTaskDelay(500);
    }
}

/**
 * Runs the tip-speed-ratio controller
 * @param pvParameters pointer to experiment setup
 */
[[noreturn]] inline void runTSRControlLoopTask(void *pvParameters)
{
    const auto experimentSetup{static_cast<ExperimentSetup *>(pvParameters)};
    constexpr int updateRateTicks{pdMS_TO_TICKS(2)};

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    const TickType_t startTime{xLastWakeTime};

    tsrController.setParameters(experimentSetup);
    const ThrustMode thrustMode{experimentSetup->thrustMode};

    if (!tsrController.enable())
    {
        blinkError();
    }

    if (thrustMode == STATIC)
    {
        tsrController.setTargetThrustCoefficient(experimentSetup->strouhalNumber, false);
        for (;;)
        {

            // tsrController.setTargetRatio(2 + 0.5f*sinf(TWO_PI * 0.7f * 0.001f* millis()));
            vTaskDelayUntil(&xLastWakeTime, updateRateTicks);
        }
    }
    // else
    tsrController.setExcitationFunction(&excitation);
    for (;;)
    {
        tsrController.setTargetThrustCoefficient(0.5463f, true);
        vTaskDelayUntil(&xLastWakeTime, updateRateTicks);
    }
}

/**
 * Runs the actuated porous disc controller
 * @param pvParameters pointer to experiment setup
 */
[[noreturn]] inline void runPDControlLoopTask(void *pvParameters)
{
    const auto experimentSetup{static_cast<ExperimentSetup *>(pvParameters)};
    // AccelStepper stepper1(AccelStepper::DRIVER, stepperStepPin, stepperDirPin);
    // const PorousDisk PD1(xPosition, yPosition, strouhalNumber, potmeterPin, &stepper1);

    TickType_t xLastWakeTime;
    const auto startTime{xTaskGetTickCount()};
    xLastWakeTime = xTaskGetTickCount();

    porousDisk.setStrouhalNumber(experimentSetup->strouhalNumber);

    if (experimentSetup->thrustMode == STATIC)
    {
        const float staticAngleDegrees{experimentSetup->strouhalNumber};
        constexpr float degToRad{0.0174532925f};
        porousDisk.setToAngleRadians(staticAngleDegrees * degToRad);
        for (;;)
        {
            vTaskDelay(10);
        }
    }

    for (;;)
    {
        // TODO: Convert to long time
        porousDisk.operatePD(millis() / 1000.0 - startTime);
    }

    porousDisk.zeroPD(nullptr);

    for (;;)
        vTaskDelay(10);
}

/**
 * Runs the sampling loop at a rate of 40Hz for a specified time as defined in the experiment setup
 * @param pvParameters Pointer to experiment setup
 */
[[noreturn]] inline void runSamplingTask(void *pvParameters)
{
    setBlinkColour(0x00FF00FF);
    const auto experimentSetup{static_cast<ExperimentSetup *>(pvParameters)};

    constexpr int updateRateTicks{pdMS_TO_TICKS(25)};
    const int sampleCount{experimentSetup->measurementTime * (1000 / updateRateTicks)};

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();

    setBlinkColour(0x00FF8000);

    vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(settlingTimeMillis));

    setBlinkColour(0x00FFFF00);

    for (int i{0}; i < sampleCount; i++)
    {
        const ExperimentMeasurement measurement{
            upstreamStrainGauge.readTaredRawData(), downstreamStrainGauge.readTaredRawData(),
            0, 0};

        SimpleLogger::log(measurement);

        vTaskDelayUntil(&xLastWakeTime, updateRateTicks);
    }

    const ExperimentMeasurement endOfSeries{0x00, -2147483648, 0x00, 0};
    SimpleLogger::log(endOfSeries);

    vTaskDelete(runControlLoopHandle);

    xTaskCreate(startExperimentTask, "startExperimentTask", 2048, nullptr, 2, &startExperimentHandle);

    vTaskDelay(100);

    vTaskDelete(runSamplingHandle);

    for (;;)
        vTaskDelay(10);
}

static bool tared{false};

/**
 * Tares the strain gauges.
 * @param pvParameters nullptr
 */
[[noreturn]] inline void tareStrainGaugesTask(void *pvParameters)
{
    tared = false;
    uint64_t upstreamTare = 0;
    uint64_t downstreamTare = 0;
    setBlinkColour(0x00FF00FF);

    constexpr int updateRateTicks{pdMS_TO_TICKS(25)};

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();

    for (int i{0}; i < tareSampleCount; i++)
    {
        upstreamTare += upstreamStrainGauge.readRawData();
        downstreamTare += downstreamStrainGauge.readRawData();

        vTaskDelayUntil(&xLastWakeTime, updateRateTicks);
    }

    upstreamTare /= tareSampleCount;
    downstreamTare /= tareSampleCount;

    upstreamStrainGauge.setTare(upstreamTare);
    downstreamStrainGauge.setTare(downstreamTare);

    vTaskDelay(100);

    tared = true;

    vTaskDelete(tareStrainGaugesHandle);

    for (;;)
        vTaskDelay(10);
}

static bool zeroed{false};

/**
 * Starting point of each measurement cycle. This task setups every task and subroutine of a measurement.
 * Starting this task starts the process of decoding the experiment setup, which in terms starts the measurement cycle.
 * @param pvParameters nullptr
 */
[[noreturn]] inline void startExperimentTask(void *pvParameters)
{
    if (!zeroed)
    {
        setBlinkColour(0x0000FF00);
        for (int i{0}; i < 900; i++)
        {
            porousDisk.zeroPD(nullptr);
            vTaskDelay(10);
        }
        porousDisk.setHome();
        zeroed = true;
    }

    porousDisk.homePD(nullptr);

    auto *pSerialCommand = new SerialCommandInterface::SerialCommand(0x00, 0x00);

    xTaskCreatePinnedToCore(SerialCommandInterface::SerialCommand::commandDecodeTask, "commandDecodeTask", 2048,
                            &pSerialCommand, 2,
                            &commandDecodeHandle, 0);

    setBlinkColour(0x000000FF);

    while (!pSerialCommand->isComplete())
        vTaskDelay(10);

    vTaskDelete(commandDecodeHandle);

    if (!pSerialCommand->convertData(&experimentSetup))
    {
        blinkError();
    }

    delete pSerialCommand;

    TaskFunction_t pvControlLoopFunction{};

    switch (experimentSetup.turbineSetup)
    {
    case POROUS_DISC:
        pvControlLoopFunction = runPDControlLoopTask;
        break;
    case MINI_TURBINE:
        pvControlLoopFunction = runTSRControlLoopTask;
        break;
    default:
        blinkError();
    }

    xTaskCreatePinnedToCore(pvControlLoopFunction, "runControlLoopTask", 2048, &experimentSetup, 3,
                            &runControlLoopHandle, 1);

    if (experimentSetup.tare)
    {
        tared = false;
        xTaskCreatePinnedToCore(tareStrainGaugesTask, "tareStrainGaugesTask", 2048, nullptr, 2, &tareStrainGaugesHandle,
                                0);
    }

    while (!tared)
        vTaskDelay(100);

    xTaskCreatePinnedToCore(runSamplingTask, "runSamplingTask", 2048, &experimentSetup, 2, &runSamplingHandle, 0);

    vTaskDelete(startExperimentHandle);

    for (;;)
        vTaskDelay(10);
}

#endif // TASKS_H
