import numpy as np
import cv2
import matplotlib.pyplot as plt
import util
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
util.setPlotStyle()

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

fig = plt.figure(figsize=[6,2.], num="PorosityThetaCurve")
gs = GridSpec(2,3, figure=fig)
ax = []
[ax.append(fig.add_subplot(gs[0, i])) for i in range(3)]
ax.append(fig.add_subplot(gs[1, :]))

[[ax[i].imshow(rot, cmap='gray_r'), ax[i].axis('off')] for i in [0, 2]]
[ax[1].imshow(img, cmap='gray_r'), ax[1].axis('off')]

ax[3].plot(Theta - Theta.mean(), por, c=util.C1)
ax[3].set(xlabel=r"$\theta$ / degree", ylabel="Porosity")
ax[3].yaxis.set_major_locator(MultipleLocator(.05))

np.save("porTheta", Theta - Theta.mean(), allow_pickle=False)
np.save("porPor", por, allow_pickle=False)

fig.savefig("./figs/theta_porosity_flat.svg")
fig.savefig("./figs/theta_porosity_flat.png")
plt.show()

