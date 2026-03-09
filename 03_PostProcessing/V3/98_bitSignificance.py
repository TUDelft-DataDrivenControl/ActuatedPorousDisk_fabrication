import matplotlib.pyplot as plt
import numpy as np

b = np.arange(17)
plt.plot(b, 2.**-b, 'x-')
plt.axhline(1e-3, ls='--', c='k')
plt.ylim([0, 1e-2])

plt.show()