import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import setPlotStyle, readData

setPlotStyle()
fig, ax = plt.subplots()

#!# Testo sensor readings
file = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\Windtunnel\5mpsSpeedSensor.csv"
df1 = pd.read_csv(file)
v1 = df1['059 [m/s]']
v1hat = np.abs(np.fft.rfft(v1))

#!# APD for theta = 0
file = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\SingleTurbine_Campaign1\Measurements\ThetaCt\PorousDisc_U_5,0_X_0,0_Y_0.json"
df2 = readData(file)
v2 = df2['UpstreamThrust']
v2f = np.fft.rfftfreq(v2.size, d=1./40.)
v2hat = np.abs(np.fft.rfft(v2))#[v2f<=.5])

p1, = ax.plot(v2f#[v2f<=.5]
              , v2hat /v2hat.max()
              , c='tab:orange', label="APD model")
p0, = ax.plot(np.fft.rfftfreq(v1.size)
              , v1hat/v1hat.max()
              , label="Anenometer")


ax.set(title="Normalised FFT magnitudes", xlim=[0,5], xlabel="freq. / Hz")
ax.legend(handles=[p0, p1])
plt.show()