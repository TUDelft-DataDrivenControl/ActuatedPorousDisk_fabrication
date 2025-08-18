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
files = getFiles(resdir+r"\Calibration Data\TSR Controller\\")
TSR_pd = readData(file=files, dir=resdir+r"\Calibration Data\TSR Controller\\")

# Unpack data
btCalData = {}
for name in TSR_pd.keys():
    TSR = str2num(name[0:-5])
    btCalData[TSR] = np.array(TSR_pd[name]['UpstreamThrust'])

# Restructure data into lists of [mass, mean, std]
BT_data = [np.array(list(btCalData.keys())), 
           np.array([strain2ct(np.array(s), J=J_BT).mean() for s in btCalData.values()]),
           np.array([strain2ct(np.array(s), J=J_BT).std() for s in btCalData.values()])]
BTsort = np.argsort(BT_data[0])

#!# Actuated Porous Disk
# Collect data DataFrames
apddir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\ThetaCt\\"
files = getFiles(apddir)
APD_pd = readData(file=files, dir=apddir)

# Unpack data
apdCalData = {}
theta = 0.
for name in APD_pd.keys():
    apdCalData[theta] = np.array(APD_pd[name]['UpstreamThrust'])
    theta += 0.5

# Restructure data into lists of [mass, mean, std]
APD_data = [np.array(list(apdCalData.keys())), 
           np.array([strain2ct(np.array(s), J=J_APD).mean() for s in apdCalData.values()]),
           np.array([strain2ct(np.array(s), J=J_APD).std() for s in apdCalData.values()])]
APDsort = np.argsort(APD_data[0])

#!# Sensor Porous disk
#!#!#!#!#!#!# DUMMY CODE - REPLACE
CtSPD = .5

#!# Data fitting
linFun = lambda x, a, b: a*x + b
polFun = lambda x, a, b, c, d: a*x**3 + b*x**2 + c*x + d

(apdKct, apdKct0), _ =  sp.optimize.curve_fit(f=linFun, xdata=APD_data[0]
                                            , ydata=APD_data[1]
                                            , sigma=APD_data[2])
(btKct3, btKct2, btKct1, btKct0), _ = (
                        sp.optimize.curve_fit(f=polFun, xdata=BT_data[0]
                                            , ydata=BT_data[1]
                                            , sigma=BT_data[2]))

#!# Save calibration
with open('CalibrationParameters', 'w') as f:
    f.write(f'''J_BT = {J_BT}
J_APD = {J_APD}
J_SPD = {J_SPD}

tsr2ct = lambda x: {btKct3}*x**3 + {btKct2}*x**2 + {btKct1}*x + {btKct0}
theta2ct = lambda x: {apdKct}*x + {apdKct0}
''')

with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters


#!# Plotting
# Plot TSR axis
fig, ax = plt.subplots(num = "CT curves")
ax.set(title="$C_T$ - curves", ylabel = "$C_T$")
ax.tick_params(axis='x', labelcolor='tab:blue')
ax.set_xlabel(xlabel = "Tip Speed Ratio", color='tab:blue')
btplot = ax.errorbar(BT_data[0][BTsort], BT_data[1][BTsort], BT_data[2][BTsort]
                      , fmt='x', elinewidth=1, markersize=3, c='tab:blue', capsize=4, label='BT - data points')

# Plot theta axis
ax2 = ax.twiny()
ax2.tick_params(axis='x', labelcolor='tab:orange')
ax2.set_xlabel(xlabel = r"$\theta$ / deg", color='tab:orange')
apdplot = ax2.errorbar(APD_data[0][APDsort], APD_data[1][APDsort], APD_data[2][APDsort]
                      , fmt='x', elinewidth=1, markersize=3, c='tab:orange', capsize=4, label='APD - data points')

ax2.grid(False), ax.grid(False)

spdplot = ax2.axhline(CtSPD, c='tab:olive', ls='--', label = "SPD")

lmd = np.linspace(BT_data[0].min(), BT_data[0].max())
theta = np.linspace(APD_data[0].min(), APD_data[0].max())
btfit, = ax.plot(lmd, tsr2ct(lmd), '--', c='tab:blue', label='BT - fit')
apdfit, = ax2.plot(theta, theta2ct(lmd), '--', c='tab:orange', label='APD - fit')

ax.legend(handles=[btplot, btfit, apdplot, apdfit, spdplot])
plt.show()