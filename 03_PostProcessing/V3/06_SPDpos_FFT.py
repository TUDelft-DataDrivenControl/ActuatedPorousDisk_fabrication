import numpy as np
from scipy.signal import welch
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
# setPlotStyle()

SPD_Y = np.array([-.5, 0., .5]) # Lateral SPD positions
SPD_X = np.array([3., 5., 7., 8., ]) # Downstream SPD positions
Dynamic_freqs = np.array([0.5, 1., 2., 3.]) # APD dynamic actuation frequencies

# filenames = getFiles(resultsFolder + "\\06_dynamic_experiments\\")
J_SPD = np.load("J_SPD.npy")
Ct_SPD = np.load("Ct_SPD.npy")

fig2, ax2 = plt.subplots(4,3, sharex=True, sharey=True, figsize=[6,3])
fig, ax = plt.subplots(4,3, sharex=True, sharey=True, figsize=[6,3])
hnd = []
fig.supylabel(r"$|\mathcal{F}\{\tilde u_r^\text{S}\}|$ for $X_{\text{SPD}}=$")
[x.set(xlabel=r"Frequency / Hz") for x in ax[-1,:]]
[x.set_ylabel(f"${p:n}D$") for x, p in zip(ax[:,0], SPD_X)]
[x.set_title(r"$Y_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[0,:], SPD_Y)]

for X, axX in zip(SPD_X, range(4)):
    for Y, axY in zip(SPD_Y, range(3)):
        for freq in Dynamic_freqs:
            npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\5mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                        allow_pickle=False)
            assert X == npzFile['spd_x'], "X location does not match file"
            assert Y == npzFile['spd_y'], "Y location does not match file"
            Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
            Y2filt = tunnel_freqs_filter(Y2)[(Nstartup+Nsettle):]

            U2 = strain2vel(Y2filt, J_SPD, Ct_SPD)

            # ax[axX, axY].semilogy(np.fft.rfftfreq(U2.size, DT)[1:], (np.abs(np.fft.rfft(U2)))[1:], 
            #                   c=f"C{int(freq)}", alpha=.6)
            f, Pxx = welch(U2, fs=1./DT, scaling='spectrum', nperseg=2**11)
            ax[axX, axY].plot(f, np.sqrt(Pxx))
            
            # ax2[axX, axY].plot(U2, 
            #                   c=f"C{int(freq)}", alpha=.6)

ax[0,0].set(xlim = [0,7])#, ylim=[5, 400])
# ax[0,0].yaxis.set_major_locator(MultipleLocator(2))
# ax[0,0].xaxis.set_major_locator(MultipleLocator(2))
plt.legend([f"{freq:1.1f} Hz" for freq in Dynamic_freqs], ncols=1, fontsize='small',
           bbox_to_anchor=(1.02, 1),
            loc='upper left', borderaxespad=0.)

# fig.savefig("./figs/spd_fft_dyn_5mps.svg")
# fig.savefig("./figs/spd_fft_dyn_5mps.png")
plt.close(fig2)
plt.show()