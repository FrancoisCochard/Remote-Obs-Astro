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
    "exposure_time_sec": 1.0,
    "settle": {
        "pixels": 1.5,
        "time": 10,
        "timeout": 60},
        
    "dither": {
        "pixels": 3.0,
        "ra_only": False}
    }
    
g = GuiderPHD2.GuiderPHD2(config=config)

g.connect_server()
print(f"Connecté ? {g.get_connected()}")
print(f"Et là, après le connect : {g.get_profiles()}")
g.connect_profile()

# On démarre les acquisitions
print("================= Acquisitions")
g.loop()
time.sleep(10)

# Pour vérifier que je peux changer le temps de pose à la volée
print("================= Exposure passe à 5s")
g.set_exposure(5.0)
time.sleep(10)

# J'active la recherche de l'étoile à la position...
print("================= Detect star")
g.find_star(200, 200, 35, 35)

# Défintion de la position de lock
print("================= Lock position")
g.set_lock_position(940, 690)

# On active le guidage
print("================= Guidage !")
g.guide()

# guide for 5 min:
for i in range(3*10):
    # ~ g.receive()
    time.sleep(1)

# Back to looping
g.loop()
print("================= Bouclage 10s")
time.sleep(10)

print("================= Fin des acquisitions")
g.stop_capture()

