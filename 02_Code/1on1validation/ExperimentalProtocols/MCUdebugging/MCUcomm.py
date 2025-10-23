import ctypes as ct
import time

def send_goto(MCU, target=0):
    if not MCU.is_open: MCU.open()

    MCU.write("GOTO".encode())
    time.sleep(.5)
    if (MCU.readline().decode() != "COMM START\r\n"):
        MCU.close()
        raise Exception("Communications start with MCU failed")
    if (MCU.readline().decode() != "GOTO RECEIVED\r\n"):
        MCU.close()
        raise Exception("Command communication with MCU failed")
    
    MCU.write(bytearray(ct.c_int16(target)))
    if (MCU.readline().decode() != str(target) + "\r\n"):
        MCU.close()
        raise Exception("Target communication with MCU failed")
    
    if (MCU.readline().decode() != "GOTO COMPLETE\r\n"):
        MCU.close()
        raise Exception("GOTO command failed to return")
    else:
        return

def send_static_measurement(MCU, duration, target):
    if not MCU.is_open: MCU.open()

    MCU.write("STRT".encode())
    time.sleep(.5)
    if (MCU.readline().decode() != "COMM START\r\n"):
        MCU.close()
        raise Exception("Communications start with MCU failed")
    if (MCU.readline().decode() != "STRT RECEIVED\r\n"):
        MCU.close()
        raise Exception("Command communication with MCU failed")
    
    MCU.write("STAT".encode())
    time.sleep(.5)
    if (MCU.readline().decode() != "STAT RECEIVED\r\n"):
        MCU.close()
        raise Exception("Command communication with MCU failed")
    
    MCU.write(bytearray(ct.c_uint64(duration)))
    if (MCU.readline().decode() != str(duration) + "\r\n"):
        MCU.close()
        raise Exception("Duration communication with MCU failed")
    
    MCU.write(bytearray(ct.c_int16(target)))
    if (MCU.readline().decode() != str(target) + "\r\n"):
        MCU.close()
        raise Exception("Target communication with MCU failed")
    
    return

def send_dynamic_measurement(MCU, duration, target):
    if not MCU.is_open: MCU.open()

    MCU.write("STRT".encode())
    time.sleep(.5)
    if (MCU.readline().decode() != "COMM START\r\n"):
        MCU.close()
        raise Exception("Communications start with MCU failed")
    if (MCU.readline().decode() != "STRT RECEIVED\r\n"):
        MCU.close()
        raise Exception("Command communication with MCU failed")
    
    MCU.write("DYNA".encode())
    time.sleep(.5)
    if (MCU.readline().decode() != "DYNA RECEIVED\r\n"):
        MCU.close()
        raise Exception("Command communication with MCU failed")
    
    MCU.write(bytearray(ct.c_uint64(duration)))
    if (MCU.readline().decode() != str(duration) + "\r\n"):
        MCU.close()
        raise Exception("Duration communication with MCU failed")
    
    for tar in target:
        MCU.write(bytearray(ct.c_int16(tar)))
    
    time.sleep(.2)
    
    for tar in target:
        if (MCU.readline().decode() != str(tar) + "\r\n"):
            MCU.close()
            raise Exception("Target communication with MCU failed")
    
    return

def receive_timeseries(MCU):
    SG1out, SG2out, Tout = [], [], []
    while MCU.in_waiting < 10:
        received = MCU.readline().decode()
        if received == "TRANSFER START\r\n":
            print(received)
            transferOngoing = True
            break
    
    while transferOngoing:
        received = MCU.readline().decode()
        if received == "SG1\r\n":
            idx = 0
            received = MCU.readline().decode()
            while received != "SG2\r\n":
                SG1out.append(int(received))
                received = MCU.readline().decode()
                idx += 1
        if received == "SG2\r\n":
            idx = 0
            received = MCU.readline().decode()
            while received != "Time\r\n":
                SG2out.append(int(received))
                received = MCU.readline().decode()
                idx += 1
        if received == "Time\r\n":
            idx = 0
            received = MCU.readline().decode()
            while received != "EXPERIMENT OK\r\n":
                Tout.append(int(received)/1000)
                received = MCU.readline().decode()
                idx += 1
        if received == "TRANSFER OK\r\n":
            print(received)
            transferOngoing = False
            MCU.close()

    return Tout, SG1out, SG2out
    