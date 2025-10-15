//
// Created by Brian on 02/05/2025.
//

#ifndef TIP_SPEED_CURVE_H
#define TIP_SPEED_CURVE_H

#include "cmath"

namespace Actuator
{
    /**
     * A struct for a degree 3 polynomial to model the tip speed ratio of a mini turbine with respect to its thrust coefficient.
     */
    struct TipSpeedCurve
    {
    private:
        const float c0;
        const float c1;
        const float c2;
        const float c3;

    public:
        TipSpeedCurve(const float c0, const float c1, const float c2, const float c3) : c0(c0), c1(c1),
            c2(c2), c3(c3)
        {
        };

        /**
         * Calculates the tip speed ratio based on a desired thrust coefficient
         * @param ct desired thrust coefficient
         * @return Tip speed ratio matching desired thrust coefficient
         */
        inline float evaluate(const float ct) const
        {
            const auto squared{ct * ct};
            const auto cubed{squared * ct};
            const auto fourth{squared * squared};

            return c0 + ct * c1 + squared * c2 + cubed * c3 + fourth;
        }
    };
}


#endif //TIP_SPEED_CURVE_H
