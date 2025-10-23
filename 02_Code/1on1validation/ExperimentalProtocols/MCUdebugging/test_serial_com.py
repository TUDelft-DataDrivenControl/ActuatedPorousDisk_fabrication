import serial

MCU = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
# MCU.open()

values = bytearray([4, 9, 62, 144, 56, 30, 147, 3, 210, 89, 111, 78, 184, 151, 17, 129])
MCU.write(values)

while True:
    while MCU.in_waiting > 0:
        print(MCU.readline().decode('utf-8'))
 
# MCU.close()