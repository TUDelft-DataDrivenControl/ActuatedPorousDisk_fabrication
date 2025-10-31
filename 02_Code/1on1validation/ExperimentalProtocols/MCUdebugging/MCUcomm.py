import ctypes as ct
import time

def send_goto(MCU, target=0, ignoreErr = False):
    if not MCU.is_open: MCU.open()

    MCU.write("GOTO".encode())
    time.sleep(.5)
    if (MCU.readline().decode() != "COMM START\r\n") and not ignoreErr:
        MCU.close()
        raise Exception("Communications start with MCU failed")
    if (MCU.readline().decode() != "GOTO RECEIVED\r\n") and not ignoreErr:
        MCU.close()
        raise Exception("Command communication with MCU failed")
    
    MCU.write(bytearray(ct.c_int16(target)))
    if (MCU.readline().decode() != str(target) + "\r\n") and not ignoreErr:
        MCU.close()
        raise Exception("Target communication with MCU failed")
    
    if (MCU.readline().decode() != "GOTO COMPLETE\r\n") and not ignoreErr:
        MCU.close()
        raise Exception("GOTO command failed to return")
    else:
        return

def send_measurement_info(MCU, target):
    duration = target.size
    if not MCU.is_open: MCU.open()

    MCU.write("STRT".encode())
    time.sleep(.005)
    cmd_echo = MCU.readline().decode()
    if (cmd_echo != "STRT RECEIVED\r\n"):
        MCU.close()
        raise Exception(f"Command communication with MCU failed, got {cmd_echo} back")
    
    MCU.write(bytearray(ct.c_uint64(duration)))
    time.sleep(.005)
    duration_echo = MCU.readline().decode()
    if (duration_echo != str(duration) + "\r\n"):
        MCU.close()
        raise Exception(f"Duration communication with MCU failed, got {duration_echo} instead of {duration}")
    
    for tar, idx1 in zip(target, range(target.size)):
        MCU.write(bytearray(ct.c_int16(tar)))
        received = MCU.readline().decode()
        if (received != str(tar) + "\r\n"):
            MCU.close()
            raise Exception(f"Target communication with MCU failed: received {received} " +
                            f"instead of {tar} at timestep {idx1}. " +
                            f"Earlier {bytearray(ct.c_int16(tar))} was sent.")
        if idx1 % 100 == 0: print(f"{int(idx1/100)} / {int(target.size/100)}")

    
    return

def receive_timeseries(MCU):
    SG1out, SG2out, Tout = [], [], []
    while True:
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
                if received == "\r\n":
                    time.sleep(0.005)
                    received = MCU.readline().decode()
                    
                idx += 1
        if received == "SG2\r\n":
            idx = 0
            received = MCU.readline().decode()
            while received != "Time\r\n":
                SG2out.append(int(received))
                received = MCU.readline().decode()
                if received == "\r\n":
                    time.sleep(0.005)
                    received = MCU.readline().decode()
                idx += 1
        if received == "Time\r\n":
            idx = 0
            received = MCU.readline().decode()
            while received != "TRANSFER OK\r\n":
                Tout.append(int(received)/1e3)
                received = MCU.readline().decode()
                if received == "\r\n":
                    time.sleep(0.005)
                    received = MCU.readline().decode()
                idx += 1
        if received == "TRANSFER OK\r\n":
            print(received)
            transferOngoing = False
            # MCU.close()

    return Tout, SG1out, SG2out
    