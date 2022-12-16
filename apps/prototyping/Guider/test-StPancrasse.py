# Generic imports
import logging
import time

# Local code
from Guider import GuiderPHD2

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s') 

# ~ config = {
    # ~ "host": "192.168.144.32",
    # ~ "port": 4400,
    # ~ # profile_id : 1 # For IRL setup
    # ~ "profile_id": 2,
    # ~ "exposure_time_sec": 2,
    # ~ "settle": {
        # ~ "pixels": 1.5,
        # ~ "time": 10,
        # ~ "timeout": 60},
        
    # ~ "dither": {
        # ~ "pixels": 3.0,
        # ~ "ra_only": False}
    # ~ }
    
config = {
    "host": "localhost",
    "port": 4400,
    "do_calibration": False,
    "profile_name": "SimulateursDistants",
    "exposure_time_sec": 2,
    "settle": {
        "pixels": 1.5,
        "time": 10,
        "timeout": 60},
    "dither": {
        "pixels": 3.0,
        "ra_only": False}
    }

g = GuiderPHD2.GuiderPHD2(config=config)
# ~ g.launch_server()
print(g.get_profiles())
g.connect()
g.get_connected()
print(g.get_profiles())
g.set_exposure(2.0)
#g.loop() not needed
g.guide()
# guide for 5 min:
for i in range(5*3):
    g.receive()
    time.sleep(1)

g.disconnect()
# ~ g.terminate_server()

# ~ g = GuiderPHD2.GuiderPHD2(config=config)
# g.launch_server()
# ~ g.connect()
# ~ g.get_connected()
# ~ print(dir(g.state))
# ~ print(f"Profiles : {g.get_profiles()}")
# ~ print(f"Connected : {g.get_connected()}")
# ~ g.set_exposure(2.0)
#g.loop() not needed
# ~ g.guide()
# guide for 5 min:
# ~ for i in range(2*5):
    # ~ g.receive()
    # ~ time.sleep(1)

# ~ g.disconnect()
# ~ g.terminate_server()
