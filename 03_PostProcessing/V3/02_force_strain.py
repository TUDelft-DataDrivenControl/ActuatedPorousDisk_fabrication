import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
setPlotStyle()

APD_filenames = getFiles(resultsFolder + "\\01_APD_SG_force_cal\\")
SPD_filenames = getFiles(resultsFolder + "\\02_SPD_SG_force_cal\\")

fig, ax = plt.subplots(figsize=[3.5,2])
ax.set(xlabel="Weight / N", ylabel="$\zeta^*$")
hnd = []

C = [C1, C2]

for extension, filenames, idx1, name in zip(["\\01_APD_SG_force_cal\\", "\\02_SPD_SG_force_cal\\"], [APD_filenames, SPD_filenames], 
                                 [1, 2], ["APD", "SPD"]):
    force, strain_mean, strain_std = [],[],[]
    for filename in filenames:
        npzFile = np.load(resultsFolder + extension + filename,
                          allow_pickle=False)
        force.append(npzFile['mass'] / 1000. * 9.81)
        strain_mean.append((npzFile[f'SG{idx1}']/bit16).mean())
        strain_std.append((npzFile[f'SG{idx1}']/bit16).std())

    linFun = lambda x, a, b: a*x + b
    linFun_std = lambda x, a_std, b_std: np.sqrt((a_std*x)**2 + b_std**2)
    (J, eps0), pcov = sp.optimize.curve_fit(f=linFun, 
                                            xdata=force, 
                                            ydata=strain_mean, 
                                            sigma=strain_std)

    hnd.append(
        ax.errorbar(x = force,
                y = strain_mean,
                yerr = strain_std ,
                fmt='x', elinewidth=1, markersize=5, capsize=4, c=C[idx1-1],
                label = name + " - data points"))
    
    X = np.arange(10) / 1000. * 9.81
    hnd.append(
        ax.plot(X, linFun(X, J, eps0), 
                c=C[idx1-1],
                label = name + " - fit",
                lw = 0.5)[0])

    np.save(f"J_{name}", J, allow_pickle=False)

    perr = np.sqrt(np.diag(pcov))
    np.save(f"J_{name}_std", perr[0], allow_pickle=False)
    CI = (J - perr[0]*2., J + perr[0]*2.)
    hnd.append(
        ax.fill_between(X,
                        linFun(X, J, eps0) + 2.*linFun_std(X, perr[0], perr[1]), 
                        linFun(X, J, eps0) - 2.*linFun_std(X, perr[0], perr[1]), 
                        color=C[idx1-1], edgecolor='none', label=name + r" - 95\% CI")
    )

    F = np.array(force)
    Y0 = np.array(strain_mean)
    Y1 = linFun(F, J, eps0)
    R2 = Rsq(Y0, Y1)
    print(rf"J_{name} = {J:1.2E} ; sigma = {perr[0]:1.2E} ; 95% CI = [{CI[0]:1.2E}, {CI[1]:1.2E}] ; fit R2 = {R2:1.2E}")

legend1 = ax.legend(handles=hnd[:3], ncol=1, fontsize='small',
           bbox_to_anchor=(.98, 0.02),
            loc='lower right', borderaxespad=0.
            )
ax.legend(handles=hnd[3:], ncol=1, fontsize='small',
           bbox_to_anchor=(.02, .98),
            loc='upper left', borderaxespad=0.
            )
ax.add_artist(legend1)
hnd[2].set_alpha(.3)
hnd[5].set_alpha(.3)
fig.savefig("./figs/force_strain.svg")
fig.savefig("./figs/force_strain.png")

plt.show()