'''
Obtain the results of the primary experiment. Put both PDs in the tunnel, you'll be
instructed where. Set the windtunnel to 5 m/s. 

Dynamic measurements will be taken for every SPD position

'''

import numpy as np
import random as rng
from MCUcomm import *
from expHelpers import *
import matplotlib.pyplot as plt

SPD_Y = np.array([-.5, 0., .5]) # Lateral SPD positions
SPD_X = np.array([7., 8., ])#3., 5., ]) # Downstream SPD positions
Dynamic_freqs = np.array([0.5, 1., 2., 3.]) # APD dynamic actuation frequencies

# for q in [SPD_Y, SPD_X, Dynamic_freqs]: rng.shuffle(q)

# Take measurements with wind
_ = input(f"Ready to sit here for {
    (25. # Taring sequence
     + 25. # Calibration
     + Tmeas * 1.2 # Data transfer and acquisition
     + 3. # saving time
     ) / 60.
     * 1.2 # Account for failure rate
     * SPD_X.size * SPD_Y.size * Dynamic_freqs.size # Nested loops
     + 1. * SPD_X.size * SPD_Y.size # SPD moving
     } minutes? [Y]")

tok = 1

for spd_x in SPD_X:
    for spd_y in SPD_Y:
        stop_wind()
        ans = ""
        while ans != "y":
            ans = input(f"Put the SPD {spd_x}D downstream and {spd_y}D laterally. Did you do it? [y / N]")
        
        moveSuccesfull = False
        while not moveSuccesfull:
            check_in = np.zeros(shape=[3*125], dtype=int)
            send_measurement_info(check_in)
            T_check, SG1_check, SG2_check = receive_timeseries()
            plt.plot(T_check, SG1_check/bit16)
            plt.plot(T_check, SG2_check/bit16)
            plt.show()
            if input("Are both PDs connected correctly? [y/N]") == "y":
                moveSuccesfull = True
        
        for freq in Dynamic_freqs:
            # Calibrate electric field without wind
            success = False
            while not success:
                try:
                    stop_wind()
                    send_goto(-150)
                    send_goto(0)
                    input("Tare and home now! [Y]")
                    MCU_in = generate_dynamic_input(fr=freq, Nmeas=int(15./DT))
                    send_measurement_info(MCU_in)
                    T, SG1, SG2 = receive_timeseries()
                    
                    fn = f"results\\06_dynamic_experiments\\0mps\\X{spd_x:1.1f}Y{spd_y:1.1f}fr{freq:1.1f}Hz.npz" # Relative path and filename
                    np.savez(file=fn, 
                             spd_x=spd_x, spd_y=spd_y, freq=freq, 
                             T=T, SG1=SG1, SG2=SG2, 
                             allow_pickle=False)
                    print(f"Saved to {fn}")
                    success = True
                except Exception as exc:
                    print(f"\033[91m EXCEPTION: {exc}\033[00m")
                finally:
                    print_divider()

        for freq in Dynamic_freqs:
            # Perform test with wind
            success = False
            while not success:
                try:
                    print(f"Trial #{tok} / {SPD_X.size * SPD_Y.size * Dynamic_freqs.size}")
                    stop_wind()
                    send_goto(-150)
                    send_goto(0)
                    input("Tare and home now! [Y]")
                    tare_in = np.zeros(shape=[5*125], dtype=int)
                    send_measurement_info(tare_in)
                    T_tare, SG1_tare, SG2_tare = receive_timeseries()

                    start_wind()
                    MCU_in = generate_dynamic_input(fr=freq)
                    send_measurement_info(MCU_in)
                    T, SG1, SG2 = receive_timeseries()
                    
                    fn = f"results\\06_dynamic_experiments\\5mps\\X{spd_x:1.1f}Y{spd_y:1.1f}fr{freq:1.1f}Hz.npz" # Relative path and filename
                    np.savez(file=fn, 
                             spd_x=spd_x, spd_y=spd_y, freq=freq, 
                             T=T, SG1=SG1, SG2=SG2, 
                             T_tare=T_tare, SG1_tare=SG1_tare, SG2_tare=SG2_tare,
                             allow_pickle=False)
                    print(f"Saved to {fn}")
                    success = True
                    tok += 1
                except Exception as exc:
                    print(f"\033[91m EXCEPTION: {exc}\033[00m")
                finally:
                    print_divider()


                
