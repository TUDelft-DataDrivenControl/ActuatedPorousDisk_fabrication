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

fig, ax = plt.subplots(3,1,figsize=[4, 3], sharex=True, sharey=True)
hnd = []
# [x.set(ylabel = f"$Y_\\text{"{"}SPD{"}"} = {y}D$, \n $\\bar u_r^\\text{"{"}S{"}"} / u_\\infty$") for x, y in zip(ax, SPD_Y)]
fig.supylabel(f"$Y_\\text{"{"}SPD{"}"} = $")
[x.set(ylabel = f"${y}D$, \n $\\bar u_r^\\text{"{"}S{"}"} / u_\\infty$") for x, y in zip(ax, SPD_Y)]
ax[-1].set(xlabel = r"$X_\text{SPD} / D$", ylim=[.5,1.])

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

hnd2 = []
# hnd2.append(ax[1].axhline(Uw_mean, c='k', ls='--', label="Mom. Th."))
# ax[1].set_xlim([2.9, 8.1])
# ax[1].fill_between(ax[1].get_xlim(), Uw_min, Uw_max, color='k', alpha=.3, edgecolor='none')
ax[0].yaxis.set_major_locator(MultipleLocator(.25))

m = ['o', 'x', '+', '1']

def Jensen(x, y, a, r0=.5, U=1.):
    f = 1 if abs(y)<.5 else 0
    return U * (1 - f * 2*a * (r0 / (r0 + .1*x))**2)

def Jensen_smeared(x, y, a, r0=.5, U=1.):
    ang = np.abs(np.arctan(y/x))
    # print(np.rad2deg(ang))
    if ang > np.deg2rad(20):
        f = 0
    else:
        f = (1 + np.cos(9*ang)) / 2
    return U * (1 - f * 2*a * (r0 / (r0 + .1*x))**2)

def Bastankhah(x, y, Ct, d0=1., U=1.):
    k = .35*.05
    b = .5 * (1 + np.sqrt(1 - Ct)) / (np.sqrt(1 - Ct))
    eps = 0.2*b
    q1 = k*x / d0 + eps
    dU = (1 - np.sqrt(1 - (Ct) / (8*q1**2))) * np.exp((-1) / (2*q1**2) * ((y/d0)**2))
    return 1 - dU

cw = np.empty([4, 4])
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
        if Y == 0. : cw[idxF, :] = U
    


fig2, ax2 = plt.subplots()
for x in SPD_X:
    for y in SPD_Y:
        Y = np.linspace(-.5, .5) + y
        # ax2.plot([Jensen_smeared(x, z, ind_mean) for z in Y], Y, 'k')
        # if y==0: ax2.axvline(np.mean([Jensen_smeared(x, z, ind_mean) for z in Y]), color='k', ls='--')
        # ax2.plot([Jensen(x, z, ind_mean) for z in Y], Y, 'k')
        ax2.plot([Bastankhah(x, z, Ct_mean) for z in Y], Y, 'k')

hnd2.append(1)
# hnd2.append(1)
for y, axY in zip(SPD_Y, range(3)):
    X = np.linspace(3., 8.)
    Y = np.linspace(-.5, .5) + y
    # Vj = [np.mean([Jensen_smeared(x, z, ind_mean) for z in Y]) for x in X]
    Vb = [np.mean([Bastankhah(x, z, Ct_mean) for z in Y]) for x in X]
    # ax[axY].fill_between(X, 
    #                      [np.mean([Jensen_smeared(x, z, ind_min) for z in Y]) for x in X], 
    #                      [np.mean([Jensen_smeared(x, z, ind_max) for z in Y]) for x in X],
    #                      color='k', alpha=.3, edgecolor='none')
    # hnd2[1] = ax[axY].plot(X, Vj, 'k-.', label="Jensen")[0]
    ax[axY].fill_between(X, 
                         [np.mean([Bastankhah(x, z, Ct_min) for z in Y]) for x in X], 
                         [np.mean([Bastankhah(x, z, Ct_max) for z in Y]) for x in X],
                         color='k', alpha=.4, edgecolor='none')
    hnd2[-1] = ax[axY].plot(X, Vb, 'k--', label="Bastankhah")[0]
    Vbcw = np.array([np.mean([Bastankhah(x, z, Ct_mean) for z in Y]) for x in SPD_X])
    if y==0. : print(f"fit R2 for centerwake Bastankhah = {Rsq(cw.mean(axis=0), Vbcw)}")


leg1 = ax[0].legend(handles=hnd[-Dynamic_freqs.size:],
          bbox_to_anchor=(.02, .02, .96, 0),
          mode = "expand",
          loc='lower left', borderaxespad=0.,
          ncols=Dynamic_freqs.size,
          fontsize='small')
leg1 = ax[-1].legend(handles=hnd2,
          bbox_to_anchor=(.02, .02),#, .96, 0),
        #   mode = "expand",
          loc='lower left', borderaxespad=0.,
          ncols=Dynamic_freqs.size)

# ax[0].legend(handles=hnd2,
#           bbox_to_anchor=(.02, 1.5, .96, 0),
#           mode = "expand",
#           loc='lower left', borderaxespad=0.,
#           ncols=len(hnd2))
# ax[0].add_artist(leg1)



plt.close(fig2)

fig.savefig("./figs/heatMap_dyn.svg")
fig.savefig("./figs/heatMap_dyn.png")
plt.show()