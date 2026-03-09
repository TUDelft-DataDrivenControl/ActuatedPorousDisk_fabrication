import numpy as np
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import vortexwake as vw
# setPlotStyle()

for freq in [0.5, 1., 2., 3.]:
    fvw_config = {'dimension': 2, 
                'time_step': .2, 
                'num_rings': 60, 
                'num_turbines': 1, 
                'num_virtual_turbines': 1,
                'turbine_positions': [[0, 0], [3., 0]],
                'vortex_core_size': 0.1}

    N = 500

    fvw = vw.VortexWake2D(fvw_config)
    states = fvw.initialise_states()
    initial_state_vector = fvw.state_vector_from_states(*states)
    controls = np.zeros((N+1, fvw.total_controls))
    # controls for the first turbine
    controls[:, fvw.yaw_idx] = 0.
    # controls for the virtual turbine
    controls[:, fvw.induction_idx + fvw.num_controls] = 0.33
    controls[:, fvw.yaw_idx + fvw.num_controls] = 0.
    inflow = np.zeros((N, fvw.dim)) + fvw.unit_vector_x *5.

    Q = np.load("c_theta.npy")
    Ct_fun = lambda theta: Q[1]*abs(theta) + Q[0] - 3.25*Q[1]
    ind_fun = lambda ct: .5 - .5*np.sqrt(1. - ct)

    T = np.arange(N+1) * fvw.time_step

    Theta = 1.5 * np.sin(2.*np.pi * freq * T) + 1.5
    # plt.plot(np.arange(Theta.size)*fvw.time_step, Theta, '--')
    Ct = Ct_fun(Theta)
    # plt.plot(np.arange(Ct.size)*fvw.time_step, Ct, '--')
    U = ind_fun(Ct)

    controls[:, fvw.induction_idx] = U

    state_history = fvw.run_forward(initial_state_vector,
                     controls,
                     inflow,
                     N,
                     with_tangent=False)[0]
    
    V = []
    for s, c in zip(state_history[0:], controls[0:, :]):
        V.append(fvw.disc_velocity(
            states = s, 
            controls = c, 
            with_tangent=False, 
            all_turbines=True
        )[0][1][0] /5)
    # plt.plot(np.arange(len(V))*fvw.time_step, U, 'k--')
    plt.plot(np.arange(len(V))*fvw.time_step, V)

plt.show()