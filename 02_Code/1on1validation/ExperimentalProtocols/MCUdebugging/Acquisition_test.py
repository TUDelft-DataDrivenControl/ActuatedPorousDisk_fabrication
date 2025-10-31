import serial
import ctypes as ct
import numpy as np
import matplotlib.pyplot as plt
from MCUcomm import *


MCU = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
PERIOD_ACQUISITION = 8


Tend = 120.
T = np.arange(Tend * 1000 / PERIOD_ACQUISITION, dtype=int)

input = np.linspace(0,125*Tend,T.size).round().astype(int) #np.zeros_like(T)
# input[0:input.size//2] = np.linspace(0,200,input.size//2).round().astype(int)

send_measurement_info(MCU, input)
# while(True):
#     print(MCU.readline().decode())
Tout, SG1out, SG2out = receive_timeseries(MCU)
Tout = np.array(Tout)

fig, ax = plt.subplots(2,1, sharex=True)
ax[0].plot(Tout - Tout[0], SG1out, "+")
ax[0].plot(Tout - Tout[0], SG2out, "+")
ax[0].set(ylabel="16 bit digital readout")#, xlabel="$t$")

ax[1].plot(Tout - Tout[0], 1./np.gradient(Tout))
ax[1].set(ylabel="Sampling freq. / Hz", xlabel="$t$")

print(Tout[-1] - Tout[0])
MCU.close()

plt.show()