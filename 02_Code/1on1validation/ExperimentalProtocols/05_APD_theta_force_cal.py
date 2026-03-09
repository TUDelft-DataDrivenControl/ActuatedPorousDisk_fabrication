'''
Get Ct-theta curve datapoints
'''

import numpy as np
import random as rng
from MCUcomm import *
from expHelpers import *

Static_theta = np.arange(0., 12.1, step=.5) - 6.
                                                # Theta values for static measurements

rng.shuffle(Static_theta)

trial = 1

for theta in Static_theta:
    success = False
    while not success:
        try:
            print(f"Working on theta = {theta}:     ({trial} / {Static_theta.size})")
            stop_wind()
            send_goto(-150)
            send_goto(0)
            input("Tare and home now! [Y]")
            stepper_target = (np.round(theta/stepAng)).astype(int)
            # Take (short) taring measurement
            send_goto(stepper_target - 150)
            send_goto(stepper_target)
            tare_in = np.ones(shape=[5*125], dtype=int) * stepper_target
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
            success = True
            trial += 1
        except Exception as exc:
            print(f"\033[91m EXCEPTION: {exc}\033[00m")
        finally:
            print_divider()

stop_wind()