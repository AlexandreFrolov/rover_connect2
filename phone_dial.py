import traceback
import pdb
import serial
import time
from sim800l import SIM800L
from rover_connect import RoverConnect

rover = RoverConnect('/dev/ttyS0', 'internet.mts.ru')
power_status = rover.power_current_status()
print("Питание: " + power_status)

creg_status = rover.creg_status()
print(creg_status)

cpin_stat = rover.cpin_status()
print(cpin_stat)

#pdb.set_trace()
#phone_number = input('Позвонить на номер телефона (+7XXXXXXXXXX):\n')
phone_number = '+79256425443'

rc = rover.dial_phone_number(phone_number)
print(rc)