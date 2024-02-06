import traceback
import pdb
import re
import time
import datetime
import json
from collections import namedtuple
from sim800l import SIM800L
from rover_connect import SmsTz
from rover_connect import RoverConnect
from rover_connect import Telemetry

if __name__ == "__main__":
#    pdb.set_trace()


    api_url = "http://dbg02-3113.itmatrix.ru:9000/api/data"
    rover = RoverConnect('/dev/ttyS0', 'internet.mts.ru')
    
    
    gsm_gnss_data = rover.getGsmLocations()
    gsm_gnss_info = gsm_gnss_data
        
    # Создаем словарь на основе данных GSMCGNSInfo
    gsm_gnss_info_data = {
        "latitude": gsm_gnss_info.latitude,
        "longitude": gsm_gnss_info.longitude,
        "msl_altitude": gsm_gnss_info.msl_altitude
    }

    # Преобразуем словарь в JSON-строку
    gsm_gnss_info_json = json.dumps(gsm_gnss_info_data, ensure_ascii=False, indent=2)  
    gsm_gnss_info_json = json.loads(gsm_gnss_info_json)        
    
     
    print(gsm_gnss_info_json)
    

    


