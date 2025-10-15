#include "LeastSquares.h"
#include <BasicLinearAlgebra.h>
#include "Calibration/AnalogCalibrationPoint.h"

namespace Interpolation
{
    /**
     * [DEPRECATED]
     * @param calibrationPoints
     * @param calibrationPointCount
     */
    LeastSquares::LeastSquares(const Calibration::AnalogCalibrationPoint* calibrationPoints,
                               const int calibrationPointCount)
    {
        float antiDiagonalValue{0};
        float bottomRightValue{0};
        float constantSolution{0};
        float linearSolution{0};

        for (int i = 0; i < calibrationPointCount; i++)
        {
            antiDiagonalValue += calibrationPoints[i].raw;
            bottomRightValue += calibrationPoints[i].raw * calibrationPoints[i].raw;
            constantSolution += calibrationPoints[i].calibrated;
            linearSolution += calibrationPoints[i].calibrated * calibrationPoints[i].raw;
        }

        const BLA::Matrix<2, 2> normalEquations{
            static_cast<float>(calibrationPointCount), antiDiagonalValue, antiDiagonalValue, bottomRightValue
        };
        const BLA::Matrix<2> solutionVector{constantSolution, linearSolution};
        BLA::Matrix<2, 2> decompositionCopy = normalEquations;
        const auto normalDecomposition = BLA::LUDecompose(decompositionCopy);
        this->coefficients = BLA::LUSolve(normalDecomposition, solutionVector);
    }

    float LeastSquares::evaluate(const float evaluationPoint) const
    {
        return (BLA::Matrix<1, 2>{1, evaluationPoint} * this->coefficients)(0);
    }
}
