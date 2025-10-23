import serial
import ctypes as ct
import numpy as np
import matplotlib.pyplot as plt
from MCUcomm import *


MCU = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
FREQ_ACQUISITION = 200

Tend = 3.
T = np.arange(Tend * FREQ_ACQUISITION) / FREQ_ACQUISITION

input = np.zeros_like(T)
input[0:input.size//2] = np.linspace(0,100,input.size//2)
SG1out = np.zeros_like(T)
SG2out = np.zeros_like(T)
Tout = np.zeros_like(T)

send_dynamic_measurement(MCU, input.size, input)
Tout, SG1out, SG2out = receive_timeseries(MCU)

fig, ax = plt.subplots(2,1, sharex=True)
ax[0].plot(Tout, SG1out)#, "|-")
ax[0].plot(Tout, SG2out)#, "|-")
ax[0].set(ylabel="16 bit digital readout")#, xlabel="$t$")

ax[1].plot(Tout, 1./np.gradient(Tout))
ax[1].set(ylabel="Sampling freq. / Hz", xlabel="$t$", ylim=[0,1.2*FREQ_ACQUISITION])

print(Tout[-1] - Tout[0])

plt.show()