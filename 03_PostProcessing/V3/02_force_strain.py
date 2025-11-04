import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
setPlotStyle()

APD_filenames = getFiles(resultsFolder + "\\01_APD_SG_force_cal\\")
SPD_filenames = getFiles(resultsFolder + "\\02_SPD_SG_force_cal\\")

fig, ax = plt.subplots()
ax.set(xlabel="Weight / N", ylabel="Normalized strain guage potential")
hnd = []

for extension, filenames, idx1, name in zip(["\\01_APD_SG_force_cal\\", "\\02_SPD_SG_force_cal\\"], [APD_filenames, SPD_filenames], 
                                 [1, 2], ["APD", "SPD"]):
    force, strain_mean, strain_std = [],[],[]
    for filename in filenames:
        npzFile = np.load(resultsFolder + extension + filename,
                          allow_pickle=False)
        force.append(npzFile['mass'] * 9.81)
        strain_mean.append((npzFile[f'SG{idx1}']/bit16).mean())
        strain_std.append((npzFile[f'SG{idx1}']/bit16).std())

    linFun = lambda x, a, b: a*x + b
    (J, eps0), _ = sp.optimize.curve_fit(f=linFun, 
                                            xdata=force, 
                                            ydata=strain_mean, 
                                            sigma=strain_std)

    hnd.append(
        ax.errorbar(x = force,
                y = strain_mean,
                yerr = strain_std ,
                fmt='x', elinewidth=1, markersize=5, capsize=4, c=f'C{idx1-1}',
                label = name + " - data points"))
    hnd.append(
        ax.plot(np.arange(10) * 9.81, np.arange(10) * 9.81*J + eps0, 
                c=f'C{idx1-1}',
                label = name + " - fit")[0])

    np.save("J_" + name, J, allow_pickle=False)

ax.legend(handles=hnd)
fig.savefig("./figs/force_strain.eps")

plt.show()