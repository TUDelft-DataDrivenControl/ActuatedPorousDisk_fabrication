#ifndef LEAST_SQUARES_H
#define LEAST_SQUARES_H

#include <BasicLinearAlgebra.h>
#include "Calibration/AnalogCalibrationPoint.h"

namespace Interpolation
{
    /**
     * [DEPRECATED]
     */
    class LeastSquares
    {
    private:
        BLA::Matrix<2> coefficients;

    public:
        LeastSquares() = default;
        LeastSquares(const Calibration::AnalogCalibrationPoint* calibrationPoints, int calibrationPointCount);
        float evaluate(float evaluationPoint) const;
    };
}

#endif //LEAST_SQUARES_H
