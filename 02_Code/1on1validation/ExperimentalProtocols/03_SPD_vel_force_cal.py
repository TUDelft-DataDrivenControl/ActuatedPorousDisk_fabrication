'''
Put the SPD in the tunnel center at 5D downstream, leave the APD outside.
'''

import numpy as np
import random as rng
import serial
from MCUcomm import *

cal_vels = np.arange(11) # Calibration weights datapoints
rng.shuffle(cal_vels) # Shuffle order, super annoying but good practise

Tmeas = 10. # s,  Measuring time
DT = 8 / 1000 # s,  Sampling period
Nsamples = (np.round(Tmeas/DT)).astype(int)

MCU_input = np.zeros(shape=[Nsamples], dtype=int) # null input

for vel in cal_vels[:]:
    ans = "" # Reset for next while loop
    while ans != "y":
        ans = input(f"Set tunnel velocity dial to {vel}. Did you do it? [y / N]")

    send_measurement_info(MCU_input)
    T, SG1, SG2 = receive_timeseries()

    velabs = 6./10.*vel
    fn = f"results\\03_SPD_vel_force_cal\\{velabs:1.2f}mps.npz" # Relative path and filename
    np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, vel=velabs, allow_pickle=False)
    print(f"Saved to {fn}")

