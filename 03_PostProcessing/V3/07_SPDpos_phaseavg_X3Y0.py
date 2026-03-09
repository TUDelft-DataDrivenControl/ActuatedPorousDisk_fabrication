import numpy as np
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
setPlotStyle()

SPD_Y = np.array([-.5, 0., .5]) # Lateral SPD positions
SPD_X = np.array([3., 5., 7., 8., ]) # Downstream SPD positions
Dynamic_freqs = np.array([0.5, 1., 2., 3.]) # APD dynamic actuation frequencies

J_SPD = np.load("J_SPD.npy")
Ct_SPD = np.load("Ct_SPD.npy")

# filenames = getFiles(resultsFolder + "\\06_dynamic_experiments\\")

fig, ax = plt.subplots(4, 1,figsize=[2, 3], sharex=True, sharey=True)
hnd = []
fig.supylabel(f"$u_r^\\text{"{"}S{"}"} / u_\\infty$")
ax[-1].set(xlabel=r"Period", xlim=[0.,1.])
# [x.set_ylabel(r"$X_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[:,0], SPD_X)]
# [x.set_title(r"$Y_{\text{SPD}}=$" + f"${p:n}D$") for x, p in zip(ax[0,:], SPD_Y)]

X, Y = 3., 0.
fs = [125, 125, 124, 123]
roller = [53, 34, 30, 30]
for freq, i in zip(Dynamic_freqs, range(4)):
    npzFile = np.load(resultsFolder + f"\\06_dynamic_experiments\\5mps\\X{X:1.1f}Y{Y:1.1f}fr{freq:1.1f}Hz.npz",
                allow_pickle=False)
    assert X == npzFile['spd_x'], "X location does not match file"
    assert Y == npzFile['spd_y'], "Y location does not match file"

    # T = npzFile['T']
    Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
    Y2filt = tunnel_freqs_filter(Y2)[(4*125):]#[(Nstartup+Nsettle):]

    # if freq > 1.:
    Tr = np.arange(Y2filt.size) * DT
    dt = 1./fs[i]
    N = round(Tr[-1]/dt)+1
    T = np.arange(N) * dt
    Y2filt = np.interp(T, Tr, Y2filt)

    Y2phAvg = strain2vel(Y2filt.reshape([-1,round(fs[i]/freq)]), J_SPD, Ct_SPD) / 5.
    print(Y2phAvg.shape)
    ax[i].axhline(Y2phAvg.mean(), color='k', ls="-.", alpha=.3)
    Y2phAvg = np.roll(Y2phAvg, -roller[i], axis=1)
    # Y2phAvg -= Y2phAvg.mean(axis=1)[:,np.newaxis]
    V2phAvg_std = Y2phAvg.std(axis=0)
    Y2phAvg = Y2phAvg.mean(axis=0)
    
    V2phAvg = Y2phAvg

    V2phAvg_std = np.append(V2phAvg_std, V2phAvg_std[0])
    V2phAvg = np.append(V2phAvg, V2phAvg[0])

    hnd.append(
    ax[i].plot(np.arange(V2phAvg.size)*dt*freq, V2phAvg, 
                        color='k',#f"C{int(freq)}",
                        label=f"{freq:1.1f} Hz")[0])
    ax[i].fill_between(np.arange(V2phAvg.size)*dt*freq, 
                        V2phAvg + 2.*V2phAvg_std, 
                        V2phAvg - 2.*V2phAvg_std, 
                        color='k',#f"C{int(freq)}", 
                        alpha=.3, edgecolor='none')
    ax[i].text(0.02, 0.7, f"\\textbf{"{"}{freq} Hz{"}"}", horizontalalignment='left',
                verticalalignment='bottom', transform=ax[i].transAxes)

x = np.arange(V2phAvg.size)*dt*freq # np.linspace(0,1, 128)
y = .59 +.04*np.cos((x - .77) *2*np.pi)
# ax[i].plot(x, y, 'r--')


cf = V2phAvg/y
L = np.polyfit(x, cf, 1)
fig2, ax2 = plt.subplots()
ax2.plot(x, cf, 'k--')
ax2.plot(x, x*L[0]+L[1], '-.')
ax2.plot(x, cf - x*L[0]-L[1] +1, 'r--')
ax2.plot(x, .02*np.cos((x*2.2+.5) *2*np.pi) +1, '-.')

plt.close(fig2)

# ax[1].legend(handles=hnd[-4:-2],
#     loc='lower right', fontsize='small')
# ax[2].legend(handles=[hnd[-2]],
#      loc='lower right', fontsize='small')
# ax[3].legend(handles=[hnd[-1]],
#      loc='lower right', fontsize='small')
# ax[0].legend(handles=hnd[-Dynamic_freqs.size:],
#           bbox_to_anchor=(.0, 1.02, 1., 0),
#           mode = "expand",
#           loc='lower left', borderaxespad=0.,
#           ncols=Dynamic_freqs.size//2)
ax[0].yaxis.set_major_locator(MultipleLocator(.05))


fig.savefig("./figs/spd_PhAvg_dyn.svg")
fig.savefig("./figs/spd_PhAvg_dyn.png")
plt.show()