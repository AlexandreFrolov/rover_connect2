import traceback
import pdb
import serial
import time
from sim800l import SIM800L
from rover_connect import RoverConnect

rover = RoverConnect('/dev/ttyS0', 'internet.mts.ru')
print("Call waiting...")
rc = rover.responce_phone_call()
print("Call from:" + rc)

"""
ata_cmd = "ATA\r\n"
ath_cmd = "ATH\r\n"

ser.flushInput()
data = ""
decoded_data = ""

try:
    while True:
      while ser.inWaiting() > 0:
        data = ser.read(ser.inWaiting())
        decoded_data = data.decode('utf-8')
        decoded_data += decoded_data

        print("get data 1: "+ decoded_data)

        time.sleep(0.0001)
      if decoded_data != "":
        print("get data 1: "+ decoded_data)
        if "RING" in decoded_data:
          ser.write(ata_cmd.encode('utf-8'))
#        if "CREG" in decoded_data:
#          print("call phone")
#          ser.write(phone.encode('utf-8'))
        decoded_data = ""
except KeyboardInterrupt:
  if ser != None:
    ser.write(ath_cmd.encode('utf-8'))
    time.sleep(0.0001)
    ser.close()
"""