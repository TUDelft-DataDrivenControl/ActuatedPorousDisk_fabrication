'''
Mount the SPD horizontally, keep the calibration weights at hand and run this script. 
'''

import numpy as np
import random as rng
from MCUcomm import *

cal_weights = np.arange(10) # Calibration weights datapoints
rng.shuffle(cal_weights) # Shuffle order, super annoying but good practise

Tmeas = 5. # s,  Measuring time
DT = 8 / 1000 # s,  Sampling period
Nsamples = (np.round(Tmeas/DT)).astype(int)

MCU_input = np.zeros(shape=[Nsamples], dtype=int) # null input

for mass in cal_weights[:]:
    ans = "" # Reset for next while loop
    while ans != "y":
        ans = input(f"Put {mass} grams on the SPD now. Did you do it? [y / N]")

    send_measurement_info(MCU_input)
    T, SG1, SG2 = receive_timeseries()

    fn = f"results\\02_SPD_SG_force_cal\\{mass}g.npz" # Relative path and filename
    np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, mass=mass, allow_pickle=False)
    print(f"Saved to {fn}")

