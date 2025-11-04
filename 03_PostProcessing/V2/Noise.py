import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from util import *
setPlotStyle()

#!# Main body
with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters
resdir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\MiniTurbineProject\Results"

#!# Bladed Turbine
# Collect data DataFrames
files = getFiles(resdir+r"\Noise Measurement\\")
TSR_pd = readData(file=files, dir=resdir+r"\Noise Measurement\\")

fig, (ax1, ax2) = plt.subplots(2, 1, num="Actuation_noise_spectra")
ax1.set(title="Bladed Turbine", xlabel="f / Hz", ylabel="$||\hat T ||$")
legList = []

# Unpack data
btCalData = {}
for name in TSR_pd.keys():
    TSR = str2num(name[0:-5])
    thrust = strain2thrust(eps=np.array(TSR_pd[name]['UpstreamThrust']), J=J_BT)
    thrustFFT = np.abs(np.fft.rfft(thrust))
    freqs = sp.fft.rfftfreq(n=thrust.size, d=1./40.)
    p, = ax1.semilogy(freqs, thrustFFT, label=f"{TSR}", alpha=.6)
    legList.append(p)

ax1.legend(handles=legList)

#!# Actuated Porous Disk
#!#!#!#!#!#!#!#!#!#!#!# ADD CODE - BASICALLY THE SAME AS BEFORE
ax2.set(title="Actuated Porous Disk", xlabel="f / Hz", ylabel="$||\hat T ||$")
legList = []


plt.show()