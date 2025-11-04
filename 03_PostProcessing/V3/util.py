import numpy as np
import os
import matplotlib.pyplot as plt

## GLOBALS
resultsFolder = r"C:\Users\sachinumans\OneDrive - Delft University of Technology\Documents\01a_Physical_Experiment\ActuatedPorousDisk_fabrication\02_Code\1on1validation\ExperimentalProtocols\results"

Tstartup = 10. # s,  Actuation startup time
Tsettle = 10. # s,  Settling time
Tmeas = 100. # s,  Measuring time

DT = 8 / 1000 # s,  Sampling period

Nstartup = (np.round(Tstartup / DT)).astype(int) # Number of startup samples
Nsettle  = (np.round(Tsettle  / DT)).astype(int) # Number of settling samples
Nmeas    = (np.round(Tmeas    / DT)).astype(int) # Number of measurement samples
Ntotal = Nstartup + Nsettle + Nmeas 

bit16 = 2**16

#!# Helper functions

def setPlotStyle():
    plt.rcParams.update({ 'text.usetex':        False,              'mathtext.fontset':         'cm',
                      'font.size':          18.0,               'axes.labelsize':           'large',
                      'xtick.labelsize':    'large',           'ytick.labelsize':          'large',
                      'axes.grid':          True,               'axes.formatter.limits':    [-3, 6],
                      'grid.alpha':         0.5,                'figure.figsize':           [10.0, 10.0/1.618],
                      'figure.constrained_layout.use': True,    'scatter.marker':           'x',
                      'savefig.dpi':        700,                'savefig.bbox':             'tight',
                      'savefig.pad_inches': 0.05,               #'savefig.transparent':      True
                      })

def getFiles(folder, excludeStr=None): 
    '''
    Get list of files in directory
    Optional: exclude files with excludeStr in their name
    '''
    folder = os.path.normpath(folder)
    if excludeStr is None: return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    else: return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and excludeStr not in f]

def strain2thrust(eps, J, eps0=0.):
    return (eps - eps0) / (J)
    
def strain2ct(eps, J, eps0=0., D=0.1, Uinf=5., rho=1.225):
    return (eps - eps0) / (J * .5 * rho * np.pi * (D/2)**2 * Uinf**2)