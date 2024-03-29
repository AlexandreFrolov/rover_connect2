#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smbus2
import bme280
import json
import time

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)
try:
    print ("Нажмите CTRL+C для завершения")
    while True:
      data = bme280.sample(bus, address, calibration_params)
      data_json = {
      "temperature": data.temperature,
      "pressure": data.pressure,
      "humidity": data.humidity
      }
      print(json.dumps(data_json))
      time.sleep(3)
except KeyboardInterrupt:
    print ("Завершено")
      