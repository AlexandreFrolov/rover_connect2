import serial
import time
import string
import pynmea2

while True:
  port="/dev/ttyS0"
  ser=serial.Serial(port, baudrate=9600, timeout=0.5)
  dataout = pynmea2.NMEAStreamReader()
  newdata=ser.readline().decode('unicode_escape')

  if newdata[0:6] == "$GPRMC":
    newmsg=pynmea2.parse(newdata)
    lat=newmsg.latitude
    lng=newmsg.longitude
    gps = "(широта, долгота): (" + str(lat) + "," + str(lng) + ")"
    print(gps)

