import numpy as np
import scipy as sp
from util import *
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

setPlotStyle()

def expon(x, a, b, c=0.):
    return a * np.exp((x - x[0]) * b) + c

def fill_window(ax, start, stop, a, b, color, c=0., label=""):
    X = np.linspace(start, stop, 200)
    return ax.fill_between(X, expon(X, a, b, c), -expon(X, a, b, c), color=color, alpha=.3, label=label)

timefig = plt.figure(num="Freq_cal_timedomain", figsize=[6,4])
gs = GridSpec(4,4, figure=timefig)
ax = []
ax.append(timefig.add_subplot(gs[0, :]))
ax.append(timefig.add_subplot(gs[1, :2]))
ax.append(timefig.add_subplot(gs[1, 2:]))
ax.append(timefig.add_subplot(gs[2, :2]))
ax.append(timefig.add_subplot(gs[2, 2:]))
ax.append(timefig.add_subplot(gs[3, :2]))
ax.append(timefig.add_subplot(gs[3, 2:]))

ax[0].set(title="system at rest")
ax[1].set(title="impulse at fan section", ylim=[-.12, .12])
ax[2].set(title="amp. demodulated response", ylim=[-1.8, 1.8])
ax[3].set(title="impulse at APD nacelle", ylim=[-.45, .45])
ax[4].set(title="amp. demodulated response", ylim=[-1.1, 1.1])
ax[5].set(title="impulse at SPD nacelle", ylim=[-.5, .5])
ax[6].set(title="amp. demodulated response", ylim=[-1.35, 1.35])

hnd = []
hndf = []

freqfig, axf = plt.subplots(3, 1, num="Freq_cal_freqdomain", sharex=True, figsize=[6,2])
# axf[0].set(title="system at rest")
# axf[1].set(title="impulse at fan section")#, ylim=[-.12, .12])
# axf[2].set(title="impulse at APD or SPD nacelle")#, ylim=[-.45, .45])
# axf[3].set(title="impulse at SPD nacelle")#, ylim=[-.5, .5])

[axf[idx].text(.01, .4, f"{a})", transform=axf[idx].transAxes) for a, idx in zip(['a', 'b', 'c'], range(3))]

## Response at rest
npzFile = np.load(resultsFolder + "\\04_freqs_cal\\RestResponse.npz",
                    allow_pickle=False)
T = (npzFile['T'] - npzFile['T'][0])/1000.
Y1 = (npzFile['SG1'] - npzFile['SG1'].mean()) / bit16
Y2 = (npzFile['SG2'] - npzFile['SG2'].mean()) / bit16
ax[0].set_xlim(T[0], T[-1])
hnd.append(
    ax[0].plot(T, Y1, c=C1, label="APD")[0]
)
hnd.append(
    ax[0].plot(T, Y2, c=C2, label="SPD")[0]
)

hndf.append(
    axf[0].plot(np.fft.rfftfreq(T.size, d=DT), np.abs(np.fft.rfft(Y1)), c=C1, label="APD")[0]
)
hndf.append(
    axf[0].plot(np.fft.rfftfreq(T.size, d=DT), np.abs(np.fft.rfft(Y2)), c=C2, label="SPD")[0]
)

## Tunnel response
npzFile = np.load(resultsFolder + "\\04_freqs_cal\\TunnelImpulseResponse.npz",
                    allow_pickle=False)
idx1 = range(125, 261)
T = (npzFile['T'][idx1] - npzFile['T'][idx1[0]])/1000.
ax[1].set_xlim(T[0], T[-1])
Y1 = (npzFile['SG1'][idx1] - npzFile['SG1'][idx1].mean()) / bit16
Y2 = (npzFile['SG2'][idx1] - npzFile['SG2'][idx1].mean()) / bit16

# hnd.append(
fill_window(ax[1], T[8 ], T[-1], .110, -3.5, color=C1, label="APD envelope")
# )
# hnd.append(
fill_window(ax[1], T[6 ], T[-1], .03, -2.5, color=C2, label="SPD envelope") 
# )
ax[1].plot(T, Y1, 'o-', c=C1, fillstyle='none')
ax[1].plot(T, Y2, 'o-', c=C2, fillstyle='none')

Y1_ = Y1[8 :-1] / expon(T[8 :-1], .11, -3.5)
Y2_ = Y2[6 :-1] / expon(T[6 :-1], .03, -2.5)
ax[2].plot(T[8 :-1], Y1_, 'o-', c=C1, fillstyle='none')
ax[2].plot(T[6 :-1], Y2_, 'o-', c=C2, fillstyle='none')

axf[1].plot(np.fft.rfftfreq(T[8 :-1].size, d=DT), np.abs(np.fft.rfft(Y1_)), c=C1)
axf[1].plot(np.fft.rfftfreq(T[6 :-1].size, d=DT), np.abs(np.fft.rfft(Y2_)), c=C2)

## Tower response
npzFile = np.load(resultsFolder + "\\04_freqs_cal\\TowerImpulseResponse.npz",
                    allow_pickle=False)
idx1 = range(1923,2069)
T = (npzFile['T'][idx1] - npzFile['T'][idx1[0]])/1000.
Y1 = (npzFile['SG1'][idx1] - npzFile['SG1'][idx1].mean()) / bit16
ax[3].set_xlim(T[0], T[-1])
fill_window(ax[3], T[0], T[-1], .3, -3.8, color=C1)
ax[3].plot(T, Y1, 'o-', c=C1, fillstyle='none')
Y1_ = Y1 / expon(T, .3, -3.8)
ax[4].plot(T, Y1_, 'o-', c=C1, fillstyle='none')
axf[2].plot(np.fft.rfftfreq(T.size, d=DT), np.abs(np.fft.rfft(Y1_)), c=C1)


idx1 = range(940,1041)
T = (npzFile['T'][idx1] - npzFile['T'][idx1[0]])/1000.
Y2 = (npzFile['SG2'][idx1] - npzFile['SG2'][idx1].mean()) / bit16
ax[5].set_xlim(T[0], T[-1])
fill_window(ax[5], T[0], T[-1], .25, -6.5, color=C2)
ax[5].plot(T, Y2, 'o-', c=C2, fillstyle='none')
Y2_ = Y2 / expon(T, .25, -6.5)
ax[6].plot(T, Y2_, 'o-', c=C2, fillstyle='none')
axf[2].plot(np.fft.rfftfreq(T.size, d=DT), np.abs(np.fft.rfft(Y2_)), c=C2)

# fig2, ax2 = plt.subplots()
# ax2.plot((npzFile['SG1'] - npzFile['SG1'].mean()) / bit16)
# ax2.plot((npzFile['SG2'] - npzFile['SG2'].mean()) / bit16)
# plt.close(freqfig)
# plt.show()

## 
timefig.suptitle("Time Domain Mechanical Calibration")
ax[0].legend(handles=hnd)
# freqfig.suptitle("Frequency Domain Mechanical Calibration")
axf[0].legend(handles=hndf)
axf[-1].set_xlabel("Frequency / Hz")
freqfig.supylabel(r"$|\mathcal{F}\{\zeta^*\}|$")
ax[-1].set_xlabel("$t$ / s")
ax[-2].set_xlabel("$t$ / s")
timefig.supylabel(r"$\zeta^*$")

timefig.savefig("./figs/freqs_cal_timeD.svg")
freqfig.savefig("./figs/freqs_cal_freqD.svg")
timefig.savefig("./figs/freqs_cal_timeD.png")
freqfig.savefig("./figs/freqs_cal_freqD.png")
plt.show()

