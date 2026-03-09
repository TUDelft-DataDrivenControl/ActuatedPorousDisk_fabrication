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

Dynamic_freqs = np.array([0., 1., 2., 3.]) # APD dynamic actuation frequencies

rng.shuffle(Dynamic_freqs)

# Take measurements without wind to obtain APD tower loading
for freq in Dynamic_freqs:
    success = False
    while not success:
        try:
            time.sleep(1.)
            send_goto(-150)
            send_goto(0)
            # input("Tare and home now! [Y]")
            MCU_in = generate_dynamic_input(fr=freq)
            send_measurement_info(MCU_in)
            T, SG1, SG2 = receive_timeseries()
            
            fn = f"results\\06_dynamic_experiments\\0mps\\fr{freq:1.1f}Hz.npz" # Relative path and filename
            np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, freq=freq, allow_pickle=False)
            print(f"Saved to {fn}")
            success = True
        except Exception as exc:
            print(f"\033[91m EXCEPTION: {exc}\033[00m")
        finally:
            print_divider()
