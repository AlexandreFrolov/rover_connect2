import traceback
import pdb
import json
from sim800l import SIM800L
from rover_connect import RoverConnect

if __name__ == "__main__":
#    pdb.set_trace()

    api_url = "http://dbg02-3113.itmatrix.ru:9000/api/data"
    rover = RoverConnect('/dev/ttyS0', 'internet.mts.ru')
    
    gnss_data = rover.get_cgns_data()
    gnss_parsed_data = rover.parse_cgns_info(gnss_data)
    gnss_parsed_data = json.loads(gnss_parsed_data)
    
    print(json.dumps(gnss_parsed_data, indent=4))
 

