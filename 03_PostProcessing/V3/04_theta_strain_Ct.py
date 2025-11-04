import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
setPlotStyle()

filenames = getFiles(resultsFolder + "\\05_APD_theta_force_cal\\")

Theta, strain_mean, strain_std = [], [], []

fig, ax = plt.subplots()
ax.set(xlabel="$\theta$ / degree", ylabel="Normalized strain guage potential")
hnd = []

for filename in filenames:
    npzFile = np.load(resultsFolder + "\\05_APD_theta_force_cal\\" + filename,
                        allow_pickle=False)
    Theta.append(npzFile['theta'])
    tare = npzFile['SG1_tare'].mean()
    strain_mean.append(((npzFile['SG1'] - tare) / bit16).mean())
    strain_std.append(((npzFile['SG1'] - tare) / bit16).std())

hnd.append(
        ax.errorbar(x = Theta,
                y = strain_mean,
                yerr = strain_std * 3,
                fmt='x', elinewidth=1, markersize=5, c='tab:blue', capsize=4,
                label = "APD - data points"))

strainLims = np.array([0., 1.])

J_APD = np.load("J_APD")
CtLims = strain2ct(strainLims, J_APD)
Ct_ax = ax.twinx()

ax.set_ylim(strainLims)
Ct_ax.set_ylim(CtLims)

# fig.savefig("./figs/theta_strain_Ct.eps")
plt.show()