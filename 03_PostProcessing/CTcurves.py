import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from util import *
setPlotStyle()

#!# Main body
with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters

# #!# Bladed Turbine
# # Collect data DataFrames
# btdir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\ThetaCt\\"
# files = getFiles(btdir)
# TSR_pd = readData(file=files, dir=btdir)

# Unpack data
# TSR = [0., 1., 1.2, 1.4, 1.6, 1.8,#
#             2., 2.2, 2.4, 2.6, 2.8,#
#             3.]
# TSR = np.arange(13)/2.
# btCalData = {}
# for idx, name in zip(range(len(TSR_pd)), TSR_pd.keys()):
#     btCalData[TSR[idx]] = np.array(TSR_pd[name]['UpstreamThrust'])

def split2windows(var=-1, data=[], Nw=1, out=None, J=None):
    wl = data.size // Nw # Window length
    print(f"Window length is {wl/40.} s")
    if out is None: out = []
    for idx in range(Nw):
        window = np.arange(wl) + idx*wl
        subdata = strain2ct(data[window], J=J)
        out.append([var, subdata.mean(), subdata.std()])
    return out


# Restructure data into lists of [TSR, mean, std]
Nw = 1
# BT_data = []
# for tsr in TSR:
#     BT_data = split2windows(var=tsr, data=btCalData[tsr], Nw=Nw, out=BT_data, J=J_BT)
# BT_data = np.array(BT_data)

#!# Actuated Porous Disk
# Collect data DataFrames
apddir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\ThetaCt\45s\\"
files = getFiles(apddir)
APD_pd = readData(file=files, dir=apddir)

# Unpack data
Theta = np.arange(13)/2.
apdCalData, apdCalDataDS = {}, {}

for idx, name in zip(range(len(APD_pd)), APD_pd.keys()):
    apdCalData[Theta[idx]] = np.array(APD_pd[name]['DownstreamThrust'])
    apdCalDataDS[Theta[idx]] = np.array(APD_pd[name]['UpstreamThrust'])

# Restructure data into lists
APD_data, APDds_data = [], []
for theta in Theta:
    APD_data = split2windows(var=theta, data=apdCalData[theta], Nw=Nw, out=APD_data, J=J_APD)
    APDds_data = split2windows(var=theta, data=apdCalDataDS[theta], Nw=Nw, out=APDds_data, J=J_SPD)
APD_data = np.array(APD_data)
APDds_data = np.array(APDds_data)


#!# Sensor Porous disk
SPD_pd = readData(file=r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\SPD_Ct\PorousDisc_U_5,0_X_0,0_Y_2.json")
CtSPD = strain2ct(np.array(SPD_pd['UpstreamThrust']), J=J_SPD).mean()

#!# Data fitting
linFun = lambda x, a, b: a*x + b
polFun = lambda x, a, b, c: a*x**2 + b*x**1 + c

apdK, _ =  sp.optimize.curve_fit(f=linFun,    xdata=APD_data[6*Nw:, 0]
                                            , ydata=APD_data[6*Nw:, 1]
                                            , sigma=APD_data[6*Nw:, 2]
                                            )
# (btKct3, btKct2, btKct1, btKct0), _ = (
#                         sp.optimize.curve_fit(f=polFun, xdata=BT_data[Nw:, 0]
#                                             , ydata=BT_data[Nw:, 1]
#                                             , sigma=BT_data[Nw:, 2]
#                                             ))

#!# Save calibration
with open('CalibrationParameters', 'w') as f:
    f.write(f'''J_APD = {J_APD}
J_SPD = {J_SPD}

theta2ct = lambda x: {apdK[0]}*x + {apdK[1]}
CT_SPD = {CtSPD}
''')

with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters


#!# Plotting
# Plot TSR axis
fig, ax2 = plt.subplots(num = "CT curves")
ax2.set(#title="$C_T$ - curves", 
        ylabel = "$C_T$")
# ax.tick_params(axis='x', labelcolor='tab:blue')
# ax.set_xlabel(xlabel = "Tip Speed Ratio", color='tab:blue')
# btplot = ax.errorbar(BT_data[Nw:, 0], BT_data[Nw:, 1], BT_data[Nw:, 2]
#                       , fmt='x', elinewidth=.1, markersize=10, c='tab:blue', capsize=2, label='BT - data points')

# Plot theta axis
# ax2 = ax.twiny()
# ax2.tick_params(axis='x', labelcolor='tab:orange')
ax2.set_xlabel(xlabel = r"$\theta$ / deg")#, color='tab:orange')
apdplot = ax2.errorbar(APD_data[:, 0], APD_data[:, 1], APD_data[:, 2]
                      , fmt='x', elinewidth=1, markersize=5, c='tab:blue', capsize=2, label='APD - data points')

# ax2.grid(False), ax.grid(False)

spdplot = ax2.axhline(CtSPD, c='tab:orange', ls='--', label = "SPD")

# lmd = np.linspace(BT_data[Nw:, 0].min(), BT_data[Nw:, 0].max())
theta = np.linspace(APD_data[6*Nw:, 0].min(), APD_data[6*Nw:, 0].max())
# btfit, = ax.plot(lmd, tsr2ct(lmd), '--', c='tab:blue', label='BT - fit')
apdfit, = ax2.plot(theta, theta2ct(theta), '--', c='tab:blue', label='APD - fit')

ax2.legend(handles=[apdplot, apdfit, spdplot])

# plt.figure()
# plt.errorbar(APDds_data[:, 0], APDds_data[:, 1], APDds_data[:, 2]
#                       , fmt='x', elinewidth=.1, markersize=10, c='tab:orange', capsize=2, label='APD - data points')

plt.show()