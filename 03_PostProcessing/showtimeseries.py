import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from util import *
setPlotStyle()

#!# Main body
with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters

SPD_pd = readData(file=r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\SPD_Ct\PorousDisc_U_5,0_X_0,0_Y_2.json")
CtSPD = strain2ct(np.array(SPD_pd['UpstreamThrust']), J=J_SPD)

plt.plot(CtSPD)
plt.show()