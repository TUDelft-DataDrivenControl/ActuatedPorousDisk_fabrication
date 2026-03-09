import numpy as np
import scipy as sp
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
    plt.rcParams.update({ 
                    'mathtext.fontset':         'cm',
                    'axes.labelsize':           'medium',
                    'xtick.labelsize':    'medium',           'ytick.labelsize':          'medium',
                    'axes.grid':          True,               'axes.formatter.limits':    [-3, 6],
                    'grid.alpha':         0.5,                'figure.figsize':           [12.0, 12.0/1.8],
                    'figure.constrained_layout.use': True,    'scatter.marker':           'x',
                    'savefig.dpi':        300,                'savefig.bbox':             'tight',
                    'savefig.pad_inches': 0.05,               #'savefig.transparent':      True,
                    # "pgf.texsystem": "pdflatex",
                    'font.family': 'serif',
                    'font.size' : 10,
                    'text.usetex': True,
                    # 'pgf.rcfonts': False,
                    'svg.fonttype': 'none',
                    'legend.fontsize': 10,
                    'text.latex.preamble': r"\usepackage{amsmath}\usepackage{amssymb}"
                      })
    
C1 = '#113B6C'
C2 = '#4FB068'

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

def strain2vel(eps, J, Ct, eps0=0., D=0.1, rho=1.225):
    return np.sqrt( 8 * (eps - eps0) / (J * rho * np.pi * D**2 * Ct) )

def tunnel_freqs_filter(X, fs=125., order=8):
    cutoff = 10. # Hz
    b, a = sp.signal.butter(N = order,
                            Wn = cutoff,
                            fs = fs,
                            btype = 'low')
    return sp.signal.lfilter(b, a, X)

def Rsq(Y0, Y1):
    # Y0: measurements, Y1: model fit
    Ymean = np.mean(Y0)
    SSres = ((Y0 - Y1)**2).sum()
    SStot = ((Y0 - Ymean)**2).sum()
    return 1 - SSres/SStot
