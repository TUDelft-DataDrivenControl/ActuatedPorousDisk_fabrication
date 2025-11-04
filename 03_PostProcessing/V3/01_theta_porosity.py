import numpy as np
import cv2
import matplotlib.pyplot as plt
import util
util.setPlotStyle()

img = cv2.imread("./PD_bw.png", cv2.IMREAD_UNCHANGED) 
img = img[:,:,-1]

h, w = img.shape[:2]  # height, width
print(h, w)
ctr = (w / 2, h / 2)
scl = 1.0

Theta = np.linspace(0., 6., 213)[3:] # in deg
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

fig, ax = plt.subplots(num="PorosityThetaCurve", figsize=[10.0, 5.0/1.618])
ax.plot(Theta, por)
ax.set(title="Porosity curve", xlabel=r"$\theta$ / degree", ylabel="Porosity")
fig.savefig("./figs/theta_porosity.eps")
plt.show()

