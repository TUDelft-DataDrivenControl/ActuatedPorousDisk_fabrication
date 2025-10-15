#ifndef ANALOG_CALIBRATION_POINT_H
#define ANALOG_CALIBRATION_POINT_H

namespace Calibration
{
    /**
     * [DEPRECATED]
     */
    struct AnalogCalibrationPoint
    {
        const float raw;
        const float calibrated;

        AnalogCalibrationPoint(const float raw, const float calibrated) : raw(raw), calibrated(calibrated)
        {
        }
    };
};

#endif //ANALOG_CALIBRATION_POINT_H
