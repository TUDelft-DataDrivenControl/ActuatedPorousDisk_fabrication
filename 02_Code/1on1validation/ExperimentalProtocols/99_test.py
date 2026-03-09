'''
Obtain the results of the primary experiment. Put both PDs in the tunnel, you'll be
instructed where. Set the windtunnel to 5 m/s. 

Dynamic measurements will be taken for every SPD position

'''

import numpy as np
import random as rng
from MCUcomm import *
from expHelpers import *
import matplotlib.pyplot as plt

Dynamic_freqs = np.array([2.]) # APD dynamic actuation frequencies

# rng.shuffle(Dynamic_freqs)

# Take measurements without wind to obtain APD tower loading
for freq in Dynamic_freqs:
    success = False
    while not success:
        try:
            time.sleep(1.)
            send_goto(-150)
            send_goto(0)
            input("Tare and home now! [Y]")
            MCU_in = generate_dynamic_input(fr=freq, Nmeas=int(80/DT))
            send_measurement_info(MCU_in)
            T, SG1, SG2 = receive_timeseries()
            success = True
        except Exception as exc:
            print(f"\033[91m EXCEPTION: {exc}\033[00m")
        finally:
            print_divider()
