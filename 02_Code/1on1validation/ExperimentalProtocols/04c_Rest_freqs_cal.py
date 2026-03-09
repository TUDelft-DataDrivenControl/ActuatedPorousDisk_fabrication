'''
Give the in situ towers an impulse by hand to retrieve the tower natural frequency.
Do not turn on the windtunnel.
'''

import numpy as np
from MCUcomm import *

Tmeas = 10. # s,  Measuring time
DT = 8 / 1000 # s,  Sampling period
Nsamples = (np.round(Tmeas/DT)).astype(int)

MCU_input = np.zeros(shape=[Nsamples], dtype=int) # null input

ans = ""
while ans != "y":
    ans = input("Just do nothing, okay? Preferably don't breathe. [y / N]")

send_measurement_info(MCU_input)
T, SG1, SG2 = receive_timeseries()

fn = "results\\04_freqs_cal\\RestResponse.npz" # Relative path and filename
np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, allow_pickle=False)
print(f"Saved to {fn}")