import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from util import *
setPlotStyle()

#!# Main body
with open('CalibrationParameters', 'r') as f: exec(f.read()) # Load calibrated parameters

apddir = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\ThetaCt\45s\\"
files = getFiles(apddir)
APD_pd = readData(file=files, dir=apddir)

#!# Filter design
# Filter parameters
cutoff_freq = 5  # Cutoff frequency in Hz
fs = 40.  # Sampling rate in Hz
order = 4  # Filter order

# Design the low-pass filter
nyq = 0.5 * fs
normal_cutoff = cutoff_freq / nyq
b, a = sp.signal.butter(order, normal_cutoff, btype='lowpass')

# Unpack data
fig, (ax, ax2, ax3) = plt.subplots(3, 1)
apdCalData = {}
theta = 0.
for name in APD_pd.keys():
    apdCalData[theta] = np.array(APD_pd[name]['UpstreamThrust'])
    T = np.arange(apdCalData[theta].size) / 40.
    ax.plot(T, apdCalData[theta], alpha=0.3, c=f"C{int(theta*2)}")
    ax2.plot(T, sp.signal.filtfilt(b, a, apdCalData[theta]), c=f"C{int(theta*2)}")
    v2f = np.fft.rfftfreq(apdCalData[theta].size, d=1./40.)
    v2hat = np.abs(np.fft.rfft(apdCalData[theta]))
    ax3.plot(v2f, v2hat, c=f"C{int(theta*2)}")
    theta += 0.5

# Restructure data into lists of [mass, mean, std]
APD_data = [np.array(list(apdCalData.keys())), 
           np.array([strain2ct(np.array(s), J=J_APD).mean() for s in apdCalData.values()]),
           np.array([strain2ct(np.array(s), J=J_APD).std() for s in apdCalData.values()])]
APDsort = np.argsort(APD_data[0])

plt.show()