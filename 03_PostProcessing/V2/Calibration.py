import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from util import *

setPlotStyle()

#!# Main body
g_ = 9.81 / 1000. # grams to newtons converter
# Collect data DataFrames
resdir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\SGcal"

filesAPD = getFiles(resdir+r"\APD\\")
filesSPD = getFiles(resdir+r"\SPD\\")
# filesBT = getFiles(resdir+r"\BT\\")
strainCalDataAPD_pd = readData(file=filesAPD, dir=resdir+r"\APD\\")
strainCalDataSPD_pd = readData(file=filesSPD, dir=resdir+r"\SPD\\")
# strainCalDataBT_pd = readData(file=filesBT, dir=resdir+r"\BT\\")

# Unpack data
strainCalData = {}
strainCalData['BT'], strainCalData['SPD'], strainCalData['APD'] = {}, {}, {}
# for name in strainCalDataBT_pd.keys():
#     m = str2num(name[-7:])
#     strainCalData['BT'][m] = np.array(strainCalDataAPD_pd[name]['UpstreamThrust'])
for name in strainCalDataSPD_pd.keys():
    m = str2num(name[-7:])
    strainCalData['SPD'][m] = np.array(strainCalDataSPD_pd[name]['UpstreamThrust'])
for name in strainCalDataAPD_pd.keys():
    m = str2num(name[-7:])
    strainCalData['APD'][m] = np.array(strainCalDataAPD_pd[name]['DownstreamThrust'])

# Restructure data into lists of [mass, mean, std]
# BT_data = [g_ * np.array(list(strainCalData['BT'].keys())), 
#            np.array([s.mean() for s in strainCalData['BT'].values()]),
#            np.array([s.std() for s in strainCalData['BT'].values()])]
# BTsort = np.argsort(BT_data[0])

APD_data = [g_ * np.array(list(strainCalData['APD'].keys())), 
           np.array([s.mean() for s in strainCalData['APD'].values()]),
           np.array([s.std() for s in strainCalData['APD'].values()])]
APDsort = np.argsort(APD_data[0])

SPD_data = [g_ * np.array(list(strainCalData['SPD'].keys())), 
           np.array([s.mean() for s in strainCalData['SPD'].values()]),
           np.array([s.std() for s in strainCalData['SPD'].values()])]
SPDsort = np.argsort(SPD_data[0])

# Linear fit on datapoints
linFun = lambda x, a, b: a*x + b

# (btJ, bt0), _ =   sp.optimize.curve_fit(f=linFun, xdata=BT_data[0]
#                                       , ydata=BT_data[1] #- BT_data[1][BTsort[-1]]
#                                       , sigma=BT_data[2])
(apdJ, apd0), _ = sp.optimize.curve_fit(f=linFun, xdata=APD_data[0]
                                      , ydata=APD_data[1] #- APD_data[1][APDsort[-1]]
                                      , sigma=APD_data[2])
(spdJ, spd0), _ = sp.optimize.curve_fit(f=linFun, xdata=SPD_data[0]
                                      , ydata=SPD_data[1] #- SPD_data[1][SPDsort[-1]]
                                      , sigma=SPD_data[2])

# Save calibration
with open('CalibrationParameters', 'w') as f:
    f.write(f'''J_APD = {apdJ}
J_SPD = {spdJ}
''')

# Plotting
fig, ax = plt.subplots(num = "Strain Calibration")
ax.set(#title="Strain Guage data for calibration weights", 
       xlabel = "Weight / N", ylabel = "Strain gauge potential / V")
# btplot = ax.errorbar(BT_data[0][BTsort], BT_data[1][BTsort]
#                     #   - BT_data[1][BTsort[-1]]
#                       , BT_data[2][BTsort]
#                       , fmt='x', elinewidth=1, markersize=5, c='tab:blue', capsize=4, label='BT - data points')
apdplot = ax.errorbar(APD_data[0][APDsort], APD_data[1][APDsort]/1e3 
                    #   - APD_data[1][APDsort[-1]]
                      , APD_data[2][APDsort] /1e3 
                      , fmt='x', elinewidth=1, markersize=5, c='tab:blue', capsize=4, label='APD - data points')
spdplot = ax.errorbar(SPD_data[0][SPDsort], SPD_data[1][SPDsort] /1e3 
                    #   - SPD_data[1][SPDsort[-1]]
                      , SPD_data[2][SPDsort]/1e3 
                      , fmt='x', elinewidth=1, markersize=5, c='tab:orange', capsize=4, label='SPD - data points')
# btfit, = ax.plot(BT_data[0][BTsort], bt0 + btJ * BT_data[0][BTsort], c='tab:blue', ls='--', label='BT - fit')
apdfit, = ax.plot(APD_data[0][APDsort], (apd0 + apdJ * APD_data[0][APDsort])/1e3 , c='tab:blue', ls='--', label='APD - fit')
spdfit, = ax.plot(SPD_data[0][SPDsort], (spd0 + spdJ * SPD_data[0][SPDsort])/1e3 , c='tab:orange', ls='--', label='SPD - fit')
ax.legend(handles=[apdplot, apdfit, spdplot, spdfit])
plt.show()