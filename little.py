import serial

ser = serial.Serial('/dev/ttyS0', 9600, 8, timeout=1)

with open("output.hex", "rb") as f:
  while True:
      data = f.read(32)
      if not data:
        break
      ser.write(data)

ser.close()