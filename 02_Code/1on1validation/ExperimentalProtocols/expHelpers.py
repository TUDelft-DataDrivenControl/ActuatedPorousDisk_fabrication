from playsound import playsound
import pyautogui
from MCUcomm import *
import numpy as np
import time

def start_wind():
    pyautogui.press('playpause')
    playsound('./StartAudio.mp3')
    pyautogui.press('playpause')
    time.sleep(3.)

def stop_wind():
    pyautogui.press('playpause')
    playsound('./StopAudio.mp3')
    pyautogui.press('playpause')
    time.sleep(3.)

Tstartup = 10. # s,  Actuation startup time
Tsettle = 10. # s,  Settling time
Tmeas = 100. # s,  Measuring time

DT = 8 / 1000 # s,  Sampling period

Nstartup = (np.round(Tstartup / DT)).astype(int) # Number of startup samples
Nsettle  = (np.round(Tsettle  / DT)).astype(int) # Number of settling samples
Nmeas    = (np.round(Tmeas    / DT)).astype(int) # Number of measurement samples
Ntotal = Nstartup + Nsettle + Nmeas 

stepAng = 0.9/32.
dynRange, dynCenter = 3., 4.5

startup_template = lambda x: 2./np.pi * np.arctan(x) + 1
startup_shape = lambda curPos, target: (startup_template(10./Nstartup * np.arange(Nstartup) - 5) - startup_template(-5)) * (target - curPos) / (startup_template(5) - startup_template(-5)) + curPos

def generate_static_input(theta, curPosAng=0.):
    curPos = (np.round(curPosAng / stepAng)).astype(int)
    target = (np.round(theta / stepAng)).astype(int) # Stepper target
    MCU_input = np.zeros(shape=[Ntotal], dtype=int) # null input
    MCU_input[:Nstartup] = (np.round(startup_shape(curPos, target))).astype(int)
    MCU_input[Nstartup:] = target
    return MCU_input

def generate_dynamic_input(fr, curPosAng=0.):
    MCU_input = generate_static_input(dynCenter-dynRange/2)

    theta = -np.cos(fr * 2*np.pi * np.arange(Nsettle+Nmeas)*DT) * dynRange/2 + dynCenter
    target = theta / stepAng # Stepper target
    MCU_input[Nstartup:] = (np.round(target)).astype(int)
    return MCU_input