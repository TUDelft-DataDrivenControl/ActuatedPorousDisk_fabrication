import numpy as np
from scipy.signal import welch
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

fig, ax = plt.subplots(4,3, sharex=True, sharey=True, figsize=[6,4])
hnd = []
fig.supylabel(r"$f_\text{APD} = $")
[x.set(xlabel=r"Frequency / Hz") for x in ax[-1,:]]
[x.set_ylabel(f"{p} Hz, \n $X_\\text{"{"}SPD{"}"} / D$") for x, p in zip(ax[:,0], Dynamic_freqs)]
[x.set_title(r"$Y_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[0,:], SPD_Y)]

for Y, axY in zip(SPD_Y, range(3)):
    for freq, axFreq in zip(Dynamic_freqs, range(4)):
        P = []
        for X, axX in zip(SPD_X, range(4)):
            npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\5mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                        allow_pickle=False)
            assert X == npzFile['spd_x'], "X location does not match file"
            assert Y == npzFile['spd_y'], "Y location does not match file"
            Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
            Y2filt = tunnel_freqs_filter(Y2)[(Nstartup+Nsettle):]

            U2 = strain2vel(Y2filt, J_SPD, Ct_SPD)

            f, Pxx = welch(U2, fs=1./DT, scaling='spectrum', nperseg=2**10)
            P.append(np.sqrt(Pxx))
        
        P = np.array(P)
        print(P.max())
        ax[axFreq, axY].grid(False)
        ax[axFreq, axY].axvline(freq, c='r', ls='--', lw=1)
        ax[axFreq, axY].pcolor(f, np.flip(SPD_X), np.flip(P, axis=0), vmin=0.03, vmax=.1, cmap='binary')
        ax[axFreq, axY].set_yticks(ticks=np.flip(SPD_X), labels=[f"${p:n}$" for p in np.flip(SPD_X)])
            
ax[0,0].set(xlim = [0,5], ylim=[2, 8.5])
ax[0,0].xaxis.set_major_locator(MultipleLocator(1.5))
plt.colorbar(ScalarMappable(norm=Normalize(vmin=0.03, vmax=.1, clip=True), cmap='binary'), ax=ax,
             extend = 'min', location = 'right', label=r"$|\mathcal{F}\{\tilde u_r^\text{S}\}|$")

fig.savefig("./figs/spd_fft_dyn_5mps.svg")
fig.savefig("./figs/spd_fft_dyn_5mps.png")
plt.show()