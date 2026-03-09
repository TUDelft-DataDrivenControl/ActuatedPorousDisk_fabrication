import numpy as np
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
setPlotStyle()

SPD_Y = np.array([-.5, 0., .5]) # Lateral SPD positions
SPD_X = np.array([3., 5., 7., 8., ]) # Downstream SPD positions
Dynamic_freqs = np.array([0.5, 1., 2., 3.]) # APD dynamic actuation frequencies

# filenames = getFiles(resultsFolder + "\\06_dynamic_experiments\\")

fig, ax = plt.subplots(4,3, sharex=True, sharey=True)
hnd = []
fig.supylabel("FFT magnitude")
[x.set(xlabel=r"Frequency / Hz") for x in ax[-1,:]]
[x.set_ylabel(r"$X_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[:,0], SPD_X)]
[x.set_title(r"$Y_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[0,:], SPD_Y)]

for X, axX in zip(SPD_X, range(4)):
    for Y, axY in zip(SPD_Y, range(3)):
        for freq in Dynamic_freqs:
            npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\0mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                        allow_pickle=False)
            assert X == npzFile['spd_x'], "X location does not match file"
            assert Y == npzFile['spd_y'], "Y location does not match file"
            Y2 = ((npzFile['SG2']) / bit16)[(Nstartup+Nsettle):]
            ax[axX, axY].plot(np.fft.rfftfreq(Y2.size, DT)[1:], np.abs(np.fft.rfft(Y2))[1:], 
                              c=f"C{int(freq)}", alpha=.6)

ax[0,0].set(xlim = [0,7])#, ylim=[0, 12])
# ax[0,0].yaxis.set_major_locator(MultipleLocator(5))
# ax[0,0].xaxis.set_major_locator(MultipleLocator(2))
ax[-1,-1].legend([f"{freq:1.1f} Hz" for freq in Dynamic_freqs], loc='upper right', ncols=2, fontsize='small')


fig.savefig("./figs/spd_fft_dyn_0mps.eps")
fig.savefig("./figs/spd_fft_dyn_0mps.png")
plt.show()