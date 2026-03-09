import numpy as np
from util import *
import matplotlib.pyplot as plt
setPlotStyle()

X = np.linspace(0.5, 1.4, 500)

# J_APD is 0.7749250581205408 +/- 0.010305569120192048 (95% CI)
# J_SPD is 0.7694094736057353 +/- 0.01478825112258205 (95% CI)
J_SPD, J_SPD_std = 0.7694094736057353, 0.01478825112258205/2. # J_SPD

# Ct = 0.8551115994261677 +/- 0.08847393140024043 (95% CI)
Ct, Ct_std = 0.8551115994261677, 0.08847393140024043/2. # Ct_SPD

N = lambda mu, sig : np.random.randn(1000)*sig + mu
G = lambda mu, sig : 1. / np.sqrt(2. * np.pi * sig**2) * np.exp(-(X-mu)**2/(2.*sig**2))

samp_J = N(J_SPD, J_SPD_std)
samp_Ct = N(Ct, Ct_std)

# https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Example_formulae

samp_Ct_J = np.array([[x * y for y in samp_Ct] for x in samp_J]).flatten()
Ct_J, Ct_J_std = J_SPD * Ct, np.sqrt(J_SPD_std**2 * Ct_std**2 + J_SPD_std**2 * Ct**2 + Ct_std**2 * J_SPD**2)

samp_invsqrt_Ct_J = samp_Ct_J**(-.5)
invsqrt_Ct_J, invsqrt_Ct_J_std = Ct_J**(-.5), np.abs(-.5 * Ct_J**(-.5 - 1.) * Ct_J_std)

fig, ax = plt.subplots()
ax.hist(samp_J, 50, density=True, alpha=.3, color="C1", label = "$J$")
ax.hist(samp_Ct, 200, density=True, alpha=.3, color="C2", label = "$C_t$")
ax.hist(samp_Ct_J,  100, density=True, alpha=.3, color="C3", label = "$J C_t$")
ax.hist(samp_invsqrt_Ct_J,  100, density=True, alpha=.3, color="C4", label = r"$(J C_t)^{-\frac{1}{2}}$")

ax.plot(X, G(J_SPD, J_SPD_std), color="C1")
ax.plot(X, G(Ct, Ct_std), color="C2")
ax.plot(X, G(Ct_J, Ct_J_std), color="C3")
ax.plot(X, G(invsqrt_Ct_J, invsqrt_Ct_J_std), color="C4")

ax.legend()

plt.show()