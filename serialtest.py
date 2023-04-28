import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, 8, timeout=1)

ser.write(b'Hello, World!')
while True:
    data = ser.readline()
    if data:
        print(data.decode('utf-8').strip())