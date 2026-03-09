'''
Put the SPD in the tunnel center at 5D downstream, leave the APD outside.
'''

import numpy as np
import random as rng
import serial
from MCUcomm import *
from expHelpers import *

cal_vels = np.arange(3, 11) # Calibration weights datapoints
cal_vels = np.append(cal_vels, [6.5, 7.5, 8.5, 9.5])
rng.shuffle(cal_vels) # Shuffle order, super annoying but good practise
print(cal_vels)

for vel in cal_vels[:]:
    pyautogui.press('playpause')
    time.sleep(1.)
    pyautogui.press('playpause')
    
    ans = "" # Reset for next while loop
    while ans != "y":
        ans = input(f"Set tunnel velocity dial to {vel}. Did you do it? [y / N]")

    success = False
    while not success:
        try:
            print(f"Working on vel = {vel}:")
            stop_wind()
            # Take (short) taring measurement
            tare_in = np.ones(shape=[5*125], dtype=int)
            send_measurement_info(tare_in)
            T_tare, SG1_tare, SG2_tare = receive_timeseries()

            # Take measurement
            start_wind()
            MCU_in = np.zeros(shape=[30 * 125], dtype=int)
            
            send_measurement_info(MCU_in)
            T, SG1, SG2 = receive_timeseries()

            velabs = 6./10.*vel
            fn = f"results\\03_SPD_vel_force_cal\\{velabs:1.2f}mps.npz" # Relative path and filename
            np.savez(file=fn, T=T, SG1=SG1, SG2=SG2, T_tare=T_tare, SG1_tare=SG1_tare, 
                    SG2_tare=SG2_tare, vel=velabs, allow_pickle=False)
            print(f"Saved to {fn}")

            success = True
        except Exception as exc:
            print(f"\033[91m EXCEPTION: {exc}\033[00m")
        finally:
            print_divider()


