import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from util import *
setPlotStyle()

#!# Main body
with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters

#!# Actuated Porous Disk
# Collect data DataFrames
apddir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\APDsinusoid\\"
files = getFiles(apddir)
APD_pd = readData(file=files, dir=apddir)

# Unpack data and plot
F = [1., 2., 3.]
apdCalData = {}

fig, ax = plt.subplots(3,1, sharex=True, sharey=True, num="PhAvg")
s = [0,0,0]
for idx, name, f in zip(range(len(APD_pd)), APD_pd.keys(), F):
    meas = np.array(APD_pd[name]['UpstreamThrust'])
    if meas.size == 4799: meas = meas[:-39]
    # meas = meas.reshape([-1,40])
    # meas = meas - meas.mean(axis=1)[:,np.newaxis]
    # s[idx] = ax[idx].plot(np.arange(40.)/40., strain2thrust(meas.mean(axis=0), J=J_SPD), label=f"{f} Hz", color=f"C{idx}")[0]
    V = np.sqrt(8. * meas / (np.pi * 1.1839 * 0.1006**2 * J_SPD * CT_SPD))
    V = V.reshape([-1,40])
    V = V - V.mean(axis=1)[:,np.newaxis]
    s[idx] = ax[idx].plot(np.arange(40.)/40., V.mean(axis=0), label=f"{f} Hz", color=f"C{idx}")[0]
    ax[idx].set_title(f"{f} Hz")

    # spread = strain2thrust(meas.std(axis=0), J=J_SPD)
    spread = V.std(axis=0)
    # ax[idx].fill_between(np.arange(40.)/40., strain2thrust(meas.mean(axis=0), J=J_SPD)-spread, strain2thrust(meas.mean(axis=0), J=J_SPD)+spread, color=f"C{idx}", alpha=.3)
    ax[idx].fill_between(np.arange(40.)/40., V.mean(axis=0) - spread, V.mean(axis=0) + spread, color=f"C{idx}", alpha=.3)

# ax[0].legend(handles=s)
# fig.suptitle("3D downstream SPD phase averaged thrust with APD upstream")
fig.supxlabel("Time / s")
fig.supylabel("Detrended eff. wind speed / (m/s)")
plt.show()