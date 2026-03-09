import ctypes as ct
import time
import numpy as np
import serial
import re

MCU = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

def send_goto(target=0):
    if not MCU.is_open: MCU.open()

    MCU.write("GOTO".encode())
    cmd_echo = MCU.readline().decode()
    while (cmd_echo == ''): cmd_echo = MCU.readline().decode()
    if (cmd_echo != "GOTO RECEIVED\r\n"):
        MCU.close()
        raise Exception(f"Command communication with MCU failed, got {cmd_echo} back")
    else: print(f"GOTO echo: {cmd_echo[:-2]}")
    
    MCU.write(bytearray(ct.c_int16(target)))
    target_echo = MCU.readline().decode()
    while (target_echo == ''): target_echo = MCU.readline().decode()
    if (target_echo != str(target) + "\r\n"):
        MCU.close()
        raise Exception("Target communication with MCU failed")
    else:print(f"Target echo: {target_echo[:-2]}")
    
    received = MCU.readline().decode()
    while (received == ''):
        received = MCU.readline().decode()
    print(f"Complete echo: {received}")
    return
    

def send_measurement_info(target):
    duration = target.size
    if not MCU.is_open: MCU.open()

    MCU.write("STRT".encode())
    cmd_echo = MCU.readline().decode()
    while (cmd_echo == ''): cmd_echo = MCU.readline().decode()
    if (cmd_echo != "STRT RECEIVED\r\n"):
        MCU.close()
        raise Exception(f"Command communication with MCU failed, got {cmd_echo} back")
    
    MCU.write(bytearray(ct.c_uint64(duration)))
    duration_echo = MCU.readline().decode()
    while (duration_echo == ''): duration_echo = MCU.readline().decode()
    if (duration_echo != str(duration) + "\r\n"):
        MCU.close()
        raise Exception(f"Duration communication with MCU failed, got {duration_echo} instead of {duration}")
    
    for tar, idx1 in zip(target, range(target.size)):
        MCU.write(bytearray(ct.c_int16(tar)))
        received = MCU.readline().decode()
        while (received == '' or received == '\r\n'): received = MCU.readline().decode()
        if (received != str(tar) + "\r\n"):
            MCU.close()
            raise Exception(f"Target communication with MCU failed: received {received} " +
                            f"instead of {tar} at timestep {idx1}. " +
                            f"Earlier {bytearray(ct.c_int16(tar))} was sent.")
        if (idx1/target.size * 100) % 10 <5e-3: print(f"{int(idx1/target.size * 100)}%")

    return

def receive_timeseries():
    while True:
        received = MCU.readline().decode()
        if received == "TRANSFER START\r\n":
            print(received[:-2])
            break
    
    data_in, tic = [], time.perf_counter()
    while received != "TRANSFER OK\r\n" and time.perf_counter()-tic < 30.:
        data_in.append(received)
        received = MCU.readline().decode()

    data_in.append(received)
    print(received[:-2])
    return decode_transfer(data_in)

def decode_transfer(data):
    print("Start data conversion")
    SG1out, SG2out, Tout = [], [], []

    fill_target = 0
    for el in data:
        if el == "SG1\r\n":
            fill_target = 'SG1'
        elif el == "SG2\r\n":
            fill_target = 'SG2'
        elif el == "Time\r\n":
            fill_target = 'T'
        elif el == "TRANSFER OK\r\n":
            print(el[:-2])
            print("End of data conversion")
            break
        
        if not checkInteger(el[:-2]): 
            print(el[:-2])
        else:
            match fill_target:
                case 'SG1':
                    SG1out.append(int(el))
                case 'SG2':
                    SG2out.append(int(el))
                case 'T':
                    Tout.append(int(el))
    
    return np.array(Tout), np.array(SG1out), np.array(SG2out)
    
def checkInteger(s):
# https://www.geeksforgeeks.org/python/check-if-string-is-integer-in-python/
    if re.match(r'^[+-]?[0-9]+$', s):
        return True
    else:
        return False

def print_divider():
    print('''
========================================================================================

''')
    return