# Generic imports
import logging
import time

# Local code
from Guider import GuiderPHD2

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s') 

config = {
    # ~ "host": "localhost",
    "host": "192.168.144.32",
    "port": 4400,
    "do_calibration": False,
    # ~ "profile_name": "Simulator",
    "profile_name": "St-Pancrasse",
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
g.launch_server()
g.connect_server()
print(f"Is server connected: {g.is_server_connected()}")
g.connect_profile()
print(f"Is profile connected: {g.is_profile_connected()} = {g.is_profile_connected(g.profile_name)}")
print(f"Currently connected equipment is {g.get_current_equipment()}")
g.set_exposure(2.0)
print("About to start looping to get images")
g.loop()
print("About to start star selection")
ret = g.find_star(x=0, y=0, width=1000, height=1000)
print(f"Return from find_star is {ret}")
print("About to set lock position")
g.set_lock_position(320.0, 350.0)
print("Lock position set")
g.guide(recalibrate=False)
# guide for 5 min:
# for i in range(5*60):
#     g.receive()
#     time.sleep(1)

# you can use set_paused in full mode (pause both looping and guiding) to test if profile disconnection works
g.set_paused(paused=True, full="full")
# you can use set_paused without full mode (looping continues, but not guiding output)
#g.set_paused(paused=True, full="")

print("Before disconnecting profile")
g.disconnect_profile()
print(f"Is profile connected: {g.is_profile_connected()} = {g.is_profile_connected(g.profile_name)}")
g.disconnect_server()
print(f"Is server connected: {g.is_server_connected()}")
g.terminate_server()
