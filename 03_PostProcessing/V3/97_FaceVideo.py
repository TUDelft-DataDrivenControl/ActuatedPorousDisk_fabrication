import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
setPlotStyle()

filenames = getFiles(resultsFolder + "\\05_APD_theta_force_cal\\")

Theta, Ct_mean, Ct_std = [], [], []
u_mean, u_std = [], []

fig, ax = plt.subplots(sharex=True, figsize=[3,1.25])
ax.set(xlabel=r"$\theta$ / degree", ylabel=r"$C_T$",
          )
hnd = []


Th = np.load("porTheta.npy")
Por = np.load("porPor.npy")

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
    
    V2db.append((8 * Y2filt / 1.225 / np.pi / 0.1006**2 / Ct_SPD / J_SPD)**.5 /5.)

hnd.append(
        ax.errorbar(x = Theta,
                y = Ct_mean,
                yerr = [s * 2. for s in Ct_std],
                fmt='x', elinewidth=1, markersize=5, c=C1, capsize=2,
                label = "APD - data points"))

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

ax.plot([-6., -3.25, 0., 3.25, 6.], [Yp, downSlope(-3.25,a), downSlope(0.,a), upSlope(3.25,a), Yp], c=C1)

ax.fill_between([-6., -3.25, 0., 3.25, 6.], 
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


ax.yaxis.set_major_locator(MultipleLocator(.05))

plt.show()