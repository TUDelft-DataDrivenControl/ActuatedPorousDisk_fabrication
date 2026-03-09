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
fig.supylabel("Normalized SG potential")
[x.set(xlabel=r"$t$ / s") for x in ax[-1,:]]
[x.set_ylabel(r"$X_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[:,0], SPD_X)]
[x.set_title(r"$Y_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[0,:], SPD_Y)]

for X, axX in zip(SPD_X, range(4)):
    for Y, axY in zip(SPD_Y, range(3)):
        for freq in Dynamic_freqs:
            npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\5mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                        allow_pickle=False)
            assert X == npzFile['spd_x'], "X location does not match file"
            assert Y == npzFile['spd_y'], "Y location does not match file"

            T = npzFile['T']
            Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
            Y2filt = tunnel_freqs_filter(Y2)[(Nstartup+Nsettle):]

            try:
                Y2phAvg = Y2filt.reshape([-1,125])
                # Y2phAvg -= Y2phAvg.mean(axis=1)[:,np.newaxis]
                Y2phAvg_std = Y2phAvg.std(axis=0)
                Y2phAvg = Y2phAvg.mean(axis=0)

                if axX==0 and axY==0:
                    hnd.append(
                    ax[axX, axY].plot(np.arange(Y2phAvg.size)*DT, Y2phAvg, 
                                        color=f"C{int(freq)}", alpha=.6,
                                        label=f"{freq:1.1f} Hz")[0])
                else:
                    ax[axX, axY].plot(np.arange(Y2phAvg.size)*DT, Y2phAvg, 
                                        color=f"C{int(freq)}", alpha=.6,
                                        label=f"{freq:1.1f} Hz")
                ax[axX, axY].fill_between(np.arange(Y2phAvg.size)*DT, 
                                          Y2phAvg + 2.*Y2phAvg_std, 
                                          Y2phAvg - 2.*Y2phAvg_std, 
                                    color=f"C{int(freq)}", alpha=.1, edgecolor='none')
            except:
                print(f"Only {Y2filt.size * DT} s measurement...")

# ax[0,0].set(xlim = [0,7], ylim=[0, 12])
# ax[0,0].yaxis.set_major_locator(MultipleLocator(5))
# ax[0,0].xaxis.set_major_locator(MultipleLocator(2))
ax[-1,-1].legend(handles=hnd, loc='lower right', ncols=2, fontsize='small')


# fig.savefig("./figs/spd_PhAvg_dyn.eps")
# fig.savefig("./figs/spd_PhAvg_dyn.png")
plt.show()