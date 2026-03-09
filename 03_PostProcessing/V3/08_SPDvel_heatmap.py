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

fig, ax = plt.subplots(figsize=[6, 2.5])
hnd = []
ax.set(xlabel = "$X / D$", ylabel = "$Y / D$",
       aspect = 'equal',
       ylim = [-.75, .75])

for X, axX in zip(SPD_X, range(4)):
    for Y, axY in zip(SPD_Y, range(3)):
        for freq, idxF in zip(Dynamic_freqs, range(Dynamic_freqs.size, 0, -1)):
            npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\5mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                        allow_pickle=False)
            assert X == npzFile['spd_x'], "X location does not match file"
            assert Y == npzFile['spd_y'], "Y location does not match file"

            T = npzFile['T']
            Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
            Y2filt = tunnel_freqs_filter(Y2)[(Nstartup+Nsettle):]

            MeanVel = strain2vel(Y2filt.mean(), J_SPD, Ct_SPD) / 5.
            
            hnd.append(
            ax.scatter(X, Y, s=3e1*idxF**1.8, c=MeanVel, cmap='Blues_r', marker='o', vmin=.5, vmax=1., edgecolors='k', linewidth=.5)
            )
            print({f" {MeanVel:1.2E}"}, end=" , ")
        print()
            
for freq, idxF in zip(Dynamic_freqs, range(Dynamic_freqs.size)):
    hnd[-idxF-1].set_label(f"{freq} Hz")
ax.legend(handles=hnd[-Dynamic_freqs.size:],
          bbox_to_anchor=(0, -.5, 1., 0),
          mode = "expand",
          loc='upper left', borderaxespad=0.,
          ncols=Dynamic_freqs.size)

ax.scatter(0,0,5e2,marker='2',c='k')
plt.colorbar(ScalarMappable(norm=Normalize(vmin=.5, vmax=1., clip=True), cmap='Blues_r'), ax=ax,
             extend = 'both', location = 'top', label=r"$\bar u_r^\text{S} / u_\infty$")

fig.savefig("./figs/heatMap_dyn.svg")
fig.savefig("./figs/heatMap_dyn.png")
plt.show()