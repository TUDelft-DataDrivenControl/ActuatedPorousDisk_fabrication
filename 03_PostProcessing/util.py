import numpy as np
import pandas
import os
import matplotlib.pyplot as plt

#!# Helper functions

def setPlotStyle():
    plt.rcParams.update({ 'text.usetex':        False,              'mathtext.fontset':         'cm',
                      'font.size':          16.0,               'axes.labelsize':           'large',
                      'xtick.labelsize':    'medium',           'ytick.labelsize':          'medium',
                      'axes.grid':          True,               'axes.formatter.limits':    [-3, 6],
                      'grid.alpha':         0.5,                'figure.figsize':           [10.0, 10.0/1.618],
                      'figure.constrained_layout.use': True,    'scatter.marker':           'x',
                      'savefig.dpi':        600,                'savefig.bbox':             'tight',
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

def readData(file, dir=""):
    '''
    Read JSON data from source
    Single file: either pass the .json address to file or specify directory and filename
                    returns a pandas DataFrame
    Multiple files: pass a list of filenames and the directory they're in
                    returns a dictionary of DataFrames
    '''    
    if type(file) is list: 
        return {f: pandas.read_json(dir+f) for f in file}
    else: 
        if not os.path.isfile(dir+file): raise FileNotFoundError(f"does not exist: {dir+file}")
        return pandas.read_json(dir+file)
    
def str2num(string):
    '''
    Remove non-numerical characters from string and cast to float
    '''
    translation_table = str.maketrans(
    '', '', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~')
    return float(string.translate(translation_table))
    
def strain2thrust(eps, J, eps0=0.):
    return (eps - eps0) / (J)
    
def strain2ct(eps, J, eps0=0., D=0.1, Uinf=5., rho=1.225):
    return (eps - eps0) / (J * .5 * rho * np.pi * (D/2)**2 * Uinf**2)