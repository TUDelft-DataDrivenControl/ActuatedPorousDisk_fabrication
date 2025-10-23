import serial
import time
import ctypes as ct

data = [1,3,2,4,-2,5, 900]

MCU = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 

for i in range(10):
    once, received = True, ""
    while received != "SENT OK\r\n":
        if (once):
            once = False
            MCU.write(bytearray(ct.c_int64(len(data))))
            for val in data:
                MCU.write(bytearray(ct.c_int16(val)))
            print("Data sent!")

        if MCU.in_waiting > 0:
            received = MCU.readline().decode('utf-8')
            print(received)
    time.sleep(.5)
 
# MCU.close()