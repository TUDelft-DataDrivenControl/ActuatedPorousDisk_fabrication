import serial
import ctypes as ct
import numpy as np
import matplotlib.pyplot as plt
from MCUcomm import *


MCU = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

send_goto(MCU, 400, ignoreErr=True)

# while(True):
#     print(MCU.readline().decode())