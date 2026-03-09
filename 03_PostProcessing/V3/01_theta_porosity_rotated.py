import numpy as np
import cv2
import matplotlib.pyplot as plt
import util
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
plt.rcParams.update({ 
                    'mathtext.fontset':         'cm',
                    'axes.labelsize':           'small',
                    'xtick.labelsize':    'small',           'ytick.labelsize':          'small',
                    'axes.grid':          True,               'axes.formatter.limits':    [-3, 6],
                    'grid.alpha':         0.5,
                    'figure.constrained_layout.use': True,    'scatter.marker':           'x',
                    'savefig.dpi':        300,                #'savefig.bbox':             'tight',
                    'savefig.pad_inches': 0.05,
                    'font.family': 'serif',
                    'font.size' : 10,
                    'text.usetex': True,
                    'svg.fonttype': 'none',
                    'legend.fontsize': 10,
                    'text.latex.preamble': r"\usepackage{amsmath}\usepackage{amssymb}"
                      })
img = cv2.imread("./PD_bw.png", cv2.IMREAD_UNCHANGED) 
img = img[:,:,-1]

h, w = img.shape[:2]  # height, width
print(h, w)
ctr = (w / 2, h / 2)
scl = 1.0

Theta = np.linspace(-6., 6., 213*2) + 12.*4 # in deg
por = np.empty_like(Theta)
A = np.pi * (w/2)**2

idx = 0
for theta in Theta:
    mat = cv2.getRotationMatrix2D(ctr, theta, scl)
    rot = cv2.warpAffine(img, mat, (w, h))
    rot += img
    rot[rot>255] = 255.
    rot = rot/255.
    por[idx] = 1. - rot.sum() / A
    idx += 1
    # cv2.imshow("Rotated Image", rot)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

fig = plt.figure(figsize=[2.5,3], num="PorosityThetaCurve")
gs = GridSpec(3,2, figure=fig)
ax = []
[ax.append(fig.add_subplot(gs[i, 1])) for i in range(3)]
ax.append(fig.add_subplot(gs[:, 0]))

[[ax[i].imshow(rot, cmap='gray_r'), ax[i].axis('off')] for i in [0, 2]]
[ax[1].imshow(img, cmap='gray_r'), ax[1].axis('off')]
[ax[i].text(.5, -0.06, fr'$\theta={a}^\circ$', horizontalalignment='center',
     verticalalignment='top', transform=ax[i].transAxes) for i, a in zip([0,1,2], [-6,0,6])]

ax[3].plot(por, Theta - Theta.mean(), c=util.C1)
ax[3].set(ylabel=r"$\theta$ / degree", xlabel="Porosity")
ax[3].xaxis.set_major_locator(MultipleLocator(.05))
ax[3].yaxis.set_major_locator(MultipleLocator(1))
ax[3].tick_params(axis='x', rotation=90)


np.save("porTheta", Theta - Theta.mean(), allow_pickle=False)
np.save("porPor", por, allow_pickle=False)

fig.savefig("./figs/theta_porosity.svg")
fig.savefig("./figs/theta_porosity.png")
plt.show()

