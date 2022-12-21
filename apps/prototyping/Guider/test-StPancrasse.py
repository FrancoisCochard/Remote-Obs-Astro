# Generic imports
import logging
import time

# Local code
from Guider import GuiderPHD2

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s') 

config = {
    "host": "192.168.144.32",
    "port": 4400,
    "profile_name": "St-Pancrasse",
    "do_calibration": False,
    "exposure_time_sec": 2,
    "settle": {
        "pixels": 1.5,
        "time": 10,
        "timeout": 60},
        
    "dither": {
        "pixels": 3.0,
        "ra_only": False}
    }
    
# ~ config = {
    # ~ "host": "localhost",
    # ~ "port": 4400,
    # ~ "do_calibration": False,
    # ~ "profile_name": "SimulateursDistants",
    # ~ "exposure_time_sec": 2,
    # ~ "settle": {
        # ~ "pixels": 1.5,
        # ~ "time": 3,
        # ~ "timeout": 60},
    # ~ "dither": {
        # ~ "pixels": 3.0,
        # ~ "ra_only": False}
    # ~ }

g = GuiderPHD2.GuiderPHD2(config=config)
# ~ g.launch_server()
# ~ print(f"Ici, avant le connect : {g.get_profiles()}")
g.connect_server()
print(f"Connecté ? {g.get_connected()}")
print(f"Et là, après le connect : {g.get_profiles()}")
g.set_exposure(2.0)
g.connect_profile(do_calibration=False)
#g.loop() not needed
print("TEST ICI ================= pas de calib !")
# ~ g.clear_calibration()
g.guide()
# guide for 5 min:
for i in range(3*1):
    # ~ g.receive()
    time.sleep(1)
# Back to looping
g.loop()
print("================= Bouclage 10s")
time.sleep(10)
print("================= Fin des acquisitions")
g.stop_capture()

# ~ g.disconnect()
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
