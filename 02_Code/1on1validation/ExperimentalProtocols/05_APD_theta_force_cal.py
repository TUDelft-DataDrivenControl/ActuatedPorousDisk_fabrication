'''
Get Ct-theta curve datapoints
'''

import numpy as np
import random as rng
import serial
from MCUcomm import *
from expHelpers import *
import time

Static_theta = np.array([0., 0.5, 1., 1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5., 5.5, 6.]) 
                                                # Theta values for static measurements

rng.shuffle(Static_theta)

send_goto()

for theta in Static_theta:
    stepper_target = (np.round(theta/stepAng)).astype(int)
    # Take (short) taring measurement
    stop_wind()
    send_goto(stepper_target)
    tare_in = np.ones(shape=[500], dtype=int) * stepper_target
    send_measurement_info(tare_in)
    T_tare, SG1_tare, SG2_tare = receive_timeseries()

    # Take static measurement
    start_wind()
    MCU_in = np.ones(shape=[Nsettle + Nmeas], dtype=int) * stepper_target
    
    send_measurement_info(MCU_in)
    T, SG1, SG2 = receive_timeseries()

    fn = f"results\\05_APD_theta_force_cal\\theta{theta:1.1f}.npz" # Relative path and filename
    np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, T_tare=T_tare, SG1_tare=SG1_tare, 
             SG2_tare=SG2_tare, theta=theta, allow_pickle=False)
    print(f"Saved to {fn}")
