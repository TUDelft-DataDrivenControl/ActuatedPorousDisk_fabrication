import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
setPlotStyle()

filenames = getFiles(resultsFolder + "\\05_APD_theta_force_cal\\")

Theta, Ct_mean, Ct_std = [], [], []
u_mean, u_std = [], []

fig, ax = plt.subplots(2,1, sharex=True, figsize=[6,3.5])
ax[0].set(ylabel=r"$C_T^\text{A}$")
ax[1].set(xlabel=r"$\theta$ / degree", ylabel=r"$u_r^\text{S}/u_\infty$",
          ylim=[.47, .77])
hnd = []

figb, axb = plt.subplots(figsize=[5,9])


Th = np.load("porTheta.npy")
Por = np.load("porPor.npy")
hnd.append(ax[0].plot(Th, -1.35*Por + 1.37, 'k--', label="De Vos")[0] )
hnd.append(ax[0].plot(Th, .85*(-1.35*Por + 1.37), 'k:', label="De Vos scaled")[0] )
# ax[0].plot(Th, .85*(-1.35*Por + 1.37), 'k:', label="De Vos")

J_APD = np.load("J_APD.npy")
J_SPD = np.load("J_SPD.npy")
Ct_SPD = np.load("Ct_SPD.npy")
V2db = []
for filename in filenames:
    npzFile = np.load(resultsFolder + "\\05_APD_theta_force_cal\\" + filename,
                        allow_pickle=False)
    # data = {a:npzFile[a] for a in npzFile.files}
    Theta.append(npzFile['theta'])
    Y1 = ((npzFile['SG1'] - npzFile['SG1_tare'].mean()) / bit16)
    Y1filt = tunnel_freqs_filter(Y1)[Nsettle:]
    Ct1 = (Y1filt) / (J_APD * .5 * 1.225 * np.pi * (.1006/2)**2 * 5.**2)
    Ct_mean.append(Ct1.mean())
    Ct_std.append(Ct1.std())

    Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
    Y2filt = tunnel_freqs_filter(Y2)[Nsettle:]

    u_mean.append(np.sqrt(8 * Y2filt.mean() / 1.225 / np.pi / 0.1006**2 / Ct_SPD / J_SPD) /5.)

    axb.plot(np.fft.rfftfreq(Y1.size, DT)[1:], np.fft.rfft(Y1)[1:])
    axb.plot(np.fft.rfftfreq(Y1filt.size, DT)[1:], np.fft.rfft(Y1filt)[1:])
    
    V2db.append((8 * Y2filt / 1.225 / np.pi / 0.1006**2 / Ct_SPD / J_SPD)**.5 /5.)

hnd.append(
        ax[0].errorbar(x = Theta,
                y = Ct_mean,
                yerr = [s * 2. for s in Ct_std],
                fmt='x', elinewidth=1, markersize=5, c=C1, capsize=4,
                label = "APD - data points"))
# hnd.append(
#     ax[1].plot(Theta, u_mean, 'x', c=C2, markersize=5,
#                 label = "SPD - mean data points")[0]
# )

viplot = ax[1].violinplot(V2db, Theta, showextrema=False, showmeans=False)
[[vip.set_color(C2)] for vip in viplot['bodies']]
# viplot['cmeans'].set_color(C2)
# viplot['cmeans'].set_label("SPD - mean")
# hnd.append(viplot['cmeans'])
hnd.append(
    ax[1].errorbar(x=Theta,
               y = [s.mean() for s in V2db],
               yerr = [s.std() * 2. for s in V2db],
                fmt='x', elinewidth=1, markersize=5, c=C2, capsize=4,
                label = "SPD - data points"))


xslope = np.array([np.abs(theta) for theta in Theta if np.abs(theta) < 3.25])
yslope = np.array([s for s, theta in zip(Ct_mean, Theta) if np.abs(theta) < 3.25])
yslope_std = np.array([s for s, theta in zip(Ct_std, Theta) if np.abs(theta) < 3.25])

yplat = np.array([s for s, theta in zip(Ct_mean, Theta) if not np.abs(theta) < 3.25])
Yp = np.mean(yplat)
Yp_std = np.std(yplat)

upSlope = lambda x, a : a * x + Yp - 3.25 * a
upSlope_std = lambda x, a_std, Yp_std : np.sqrt(((x - 3.25) * a_std)**2 + Yp_std**2)
downSlope = lambda x, a : -a * x + Yp - 3.25 * a
downSlope_std = lambda x, a_std, Yp_std : np.sqrt(((-x - 3.25) * a_std)**2 + Yp_std**2)
a = sp.optimize.curve_fit(f=upSlope, 
                            xdata=xslope, 
                            ydata=yslope, 
                            sigma=yslope_std
                            )

a_std = np.sqrt(a[1][0][0])
a = a[0][0]

CI = (Yp - Yp_std*2., Yp + Yp_std*2.)
print(rf"c_0 = {Yp:1.2E} ; sigma = {Yp_std:1.2E} ; 95% CI = [{CI[0]:1.2E}, {CI[1]:1.2E}]")
CI = (a - a_std*2., a + a_std*2.)
print(rf"c_1 = {a:1.2E} ; sigma = {a_std:1.2E} ; 95% CI = [{CI[0]:1.2E}, {CI[1]:1.2E}]")


def fitted(X):
    Y = np.empty_like(X)
    for x, i in zip(X, range(len(X))):
        if abs(x) >= 3.25:
            Y[i] = Yp
        else:
            Y[i] = a*abs(x) + Yp - 3.25*a
    return Y

F = np.array(Theta)
Y0 = np.array(Ct_mean)
Y1 = fitted(F)
R2 = Rsq(Y0, Y1)
print(f"Fit R2 = {R2:1.2E}")

ax[0].plot([-6., -3.25, 0., 3.25, 6.], [Yp, downSlope(-3.25,a), downSlope(0.,a), upSlope(3.25,a), Yp], c=C1)

ax[0].fill_between([-6., -3.25, 0., 3.25, 6.], 
                [Yp + 2.*Yp_std,
                 downSlope(-3.25,a) + 2.*downSlope_std(-3.25, a_std, Yp_std),
                 downSlope(0.,a) + 2.*downSlope_std(0., a_std, Yp_std),
                 upSlope(3.25,a) + 2.*upSlope_std(3.25, a_std, Yp_std),
                 Yp + 2.*Yp_std], 
                [Yp - 2.*Yp_std,
                 downSlope(-3.25,a) - 2.*downSlope_std(-3.25, a_std, Yp_std),
                 downSlope(0.,a) - 2.*downSlope_std(0., a_std, Yp_std),
                 upSlope(3.25,a) - 2.*upSlope_std(3.25, a_std, Yp_std),
                 Yp - 2.*Yp_std],
                color=C1, alpha=.3, edgecolor='none')

[ax[i].text(0.01, 0.8, f"\\textbf{"{"}{q}){"}"}", horizontalalignment='left',
                verticalalignment='bottom', transform=ax[i].transAxes) for q,i in zip(['a', 'b'], range(2))]
ax[0].yaxis.set_major_locator(MultipleLocator(.05))
ax[1].yaxis.set_major_locator(MultipleLocator(.05))
# leg1 = ax[0].legend(handles=[hnd[2]], loc="lower right")
# leg2 = ax[0].legend(handles=[hnd[0]], loc="upper center")
# ax[0].legend(handles=[hnd[1]], loc="lower left")
# ax[0].add_artist(leg1)
# ax[0].add_artist(leg2)
ax[0].legend(handles=hnd[:-1],
          bbox_to_anchor=(.02, 1.02, .96, 0),
          mode = "expand",
          loc='lower left', borderaxespad=0.,
          ncols=len(hnd[:-1]))
ax[1].legend(handles=[hnd[3]], loc='upper right')

plt.close(figb)
c = [Yp, a]
np.save("c_theta", c, allow_pickle=False)

fig.savefig("./figs/theta_strain_Ct.svg")
fig.savefig("./figs/theta_strain_Ct.png")
plt.show()