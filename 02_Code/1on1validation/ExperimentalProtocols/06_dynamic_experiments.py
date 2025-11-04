'''
Obtain the results of the primary experiment. Put both PDs in the tunnel, you'll be
instructed where. Set the windtunnel to 5 m/s. 

Dynamic measurements will be taken for every SPD position

'''

import numpy as np
import random as rng
from MCUcomm import *
from expHelpers import *

SPD_Y = np.array([0., .5]) # Lateral SPD positions
SPD_X = np.array([3., 5., 7., 8.]) # Downstream SPD positions
Dynamic_freqs = np.array([1., 2., 3.]) # APD dynamic actuation frequencies

for q in [SPD_Y, SPD_X, Dynamic_freqs]: rng.shuffle(q)

# Take measurements without wind to obtain APD tower loading
stop_wind()
for freq in Dynamic_freqs:
    send_goto()
    MCU_in = generate_dynamic_input(fr=freq, curPosAng=0.)
    send_measurement_info(MCU_in)
    T, SG1, SG2 = receive_timeseries()
    
    fn = f"results\\06_dynamic_experiments\\0mps\\fr{freq:1.1f}Hz.npz" # Relative path and filename
    np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, freq=freq, allow_pickle=False)
    print(f"Saved to {fn}")

start_wind()
# Take measurements with wind
for spd_x in SPD_X:
    for spd_y in SPD_Y:
        ans = ""
        while ans != "y":
            ans = input(f"Put the SPD {spd_x}D downstream and {spd_y}D laterally. Did you do it? [y / N]")
            for freq in Dynamic_freqs:
                send_goto()
                MCU_in = generate_dynamic_input(fr=freq, curPosAng=0.)
                send_measurement_info(MCU_in)
                T, SG1, SG2 = receive_timeseries()
                
                fn = f"results\\06_dynamic_experiments\\5mps\\fr{freq:1.1f}Hz.npz" # Relative path and filename
                np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, freq=freq, allow_pickle=False)
                print(f"Saved to {fn}")

                
