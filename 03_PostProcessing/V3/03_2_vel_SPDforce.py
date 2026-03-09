import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
setPlotStyle()

filenames = getFiles(resultsFolder + "\\03_SPD_vel_force_cal\\")

vel, strain_mean, strain_std = [], [], []

fig, ax = plt.subplots(figsize=[6,2.])
ax.set(xlabel=r"$u_\infty$ / m s${}^{-1}$", ylabel=r"$\zeta$")
hnd, data = [], []

figb, axb = plt.subplots()

for filename, idx in zip(filenames, range(len(filenames))):
    npzFile = np.load(resultsFolder + "\\03_SPD_vel_force_cal\\" + filename,
                        allow_pickle=False)
    if npzFile['vel'] <= 2: continue
    vel.append(npzFile['vel'])
    Y2 = ((npzFile['SG2'] - npzFile['SG2_tare'].mean()) / bit16)
    Y2filt = tunnel_freqs_filter(Y2)[Nstartup:]
    # data.append({a:npzFile[a] for a in npzFile.files})

    strain_mean.append(Y2filt.mean())
    strain_std.append(Y2filt.std() * 2.)

    axb.plot(np.fft.rfftfreq(Y2.size, DT), np.fft.rfft(Y2))
    axb.plot(np.fft.rfftfreq(Y2filt.size, DT), np.fft.rfft(Y2filt))

hnd.append(
        ax.errorbar(x = vel,
                y = strain_mean,
                yerr = strain_std,
                fmt='x', elinewidth=1, markersize=5, c=C2, capsize=4,
                label = "Data points"))

strainLims = np.array([0., .08])

J_SPD = np.load("J_SPD.npy")
J_SPD_std = np.load("J_SPD_std.npy")

fitFun = lambda u, Ct: 1.225 * np.pi * 0.1006**2 * u**2 * J_SPD * Ct / 8
popt, pcov, = sp.optimize.curve_fit(f=fitFun, 
                                        xdata=vel, 
                                        ydata=strain_mean, 
                                        sigma=strain_std)

perr = np.sqrt(np.diag(pcov))
Ct_std = perr[0]
Ct = popt[0]
CI = (Ct - Ct_std*2., Ct + Ct_std*2.)
hnd.append(
ax.plot(np.linspace(0., vel[-1], 200), fitFun(np.linspace(0., vel[-1], 200), Ct), c=C2,
                label = "Quadratic fit")[0])
vel = np.array(vel)

U = np.linspace(0,vel.max())
c1 = 1.225 * np.pi * 0.1006**2 * U**2 / 8

Ct_J, Ct_J_std = J_SPD * Ct, np.sqrt(J_SPD_std**2 * Ct_std**2 + J_SPD_std**2 * Ct**2 + Ct_std**2 * J_SPD**2)

hnd.append(
    ax.fill_between(U,
                c1 * (Ct * J_SPD + 2.*Ct_J_std),
                c1 * (Ct * J_SPD - 2.*Ct_J_std),
                color=C2, edgecolor='none',
                label=r"95\% CI"))

ax.legend(handles=hnd)
hnd[-1].set_alpha(.3)

F = np.array(vel)
Y0 = np.array(strain_mean)
Y1 = fitFun(F, Ct)
R2 = Rsq(Y0, Y1)
print(rf"Ct_SPD = {Ct:1.2E} ; sigma = {Ct_std:1.2E} ; 95% CI = [{CI[0]:1.2E}, {CI[1]:1.2E}] ; fit R2 = {R2:1.2E}")

np.save(f"Ct_SPD", Ct, allow_pickle=False)
np.save(f"Ct_SPD_std", Ct_std, allow_pickle=False)
np.save("Ct_J_SPD_std", Ct_J_std, allow_pickle=False)

fig.savefig("./figs/vel_SPDstrain.svg")
fig.savefig("./figs/vel_SPDstrain.png")

plt.close(fig=figb)
plt.show()