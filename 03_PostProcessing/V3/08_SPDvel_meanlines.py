import numpy as np
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
setPlotStyle()

SPD_Y = np.array([-.5, 0., .5]) # Lateral SPD positions
SPD_X = np.array([3., 5., 7., 8., ]) # Downstream SPD positions
Dynamic_freqs = np.array([0.5, 1., 2., 3.]) # APD dynamic actuation frequencies

J_SPD = np.load("J_SPD.npy")
Ct_SPD = np.load("Ct_SPD.npy")

fig, ax = plt.subplots(3,1,figsize=[6, 3.5], sharex=True, sharey=True)
hnd = []
[x.set(ylabel = f"$Y_\\text{"{"}SPD{"}"} = {y}D$, \n $\\bar u_r^\\text{"{"}S{"}"} / u_\\infty$") for x, y in zip(ax, SPD_Y)]
ax[-1].set(xlabel = "$X / D$", ylim=[.5,1.])

c = np.load("c_theta.npy")
Ct_min  = c[1]*abs(0.0) + c[0] - 3.25*c[1]
Ct_mean = c[1]*abs(1.5) + c[0] - 3.25*c[1]
Ct_max  = c[1]*abs(3.0) + c[0] - 3.25*c[1]

ind_min  = .5 - .5*np.sqrt(1 - Ct_min)
ind_mean = .5 - .5*np.sqrt(1 - Ct_mean)
ind_max  = .5 - .5*np.sqrt(1 - Ct_max)

Uw_min  = 1 - 2*ind_min
Uw_mean = 1 - 2*ind_mean
Uw_max  = 1 - 2*ind_max

ax[1].axhline(Uw_mean, c='k', ls='--')
ax[1].set_xlim([2.9, 8.1])
ax[1].fill_between(ax[1].get_xlim(), Uw_min, Uw_max, color='k', alpha=.2, edgecolor='none')
ax[0].yaxis.set_major_locator(MultipleLocator(.1))

m = ['o', 'x', '+', '1']

for Y, axY in zip(SPD_Y, range(3)):
    for freq, idxF in zip(Dynamic_freqs, range(Dynamic_freqs.size)):
        U = []
        for X, axX in zip(SPD_X, range(4)):
            npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\5mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                        allow_pickle=False)
            assert X == npzFile['spd_x'], "X location does not match file"
            assert Y == npzFile['spd_y'], "Y location does not match file"

            T = npzFile['T']
            Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
            Y2filt = tunnel_freqs_filter(Y2)[(Nstartup+Nsettle):]

            MeanVel = strain2vel(Y2filt.mean(), J_SPD, Ct_SPD) / 5.
            
            U.append(MeanVel)
        hnd.append(ax[axY].plot(SPD_X, U, f'{m[idxF]}-', label=f"{freq} Hz")[0])
    

ax[0].legend(handles=hnd[-Dynamic_freqs.size:],
          bbox_to_anchor=(0, 1.1, 1., 0),
          mode = "expand",
          loc='lower left', borderaxespad=0.,
          ncols=Dynamic_freqs.size)

fig.savefig("./figs/heatMap_dyn.svg")
fig.savefig("./figs/heatMap_dyn.png")
plt.show()