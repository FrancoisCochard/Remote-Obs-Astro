# ~ Juillet 2023 : petit test de PHD2 guiding
# ~ Je suis en mode simulateur
# ~ Je points Cor Carolis
# ~ Puis je sélectionne l'étoile au milieu de l'image
# ~ Puis je lance le guidage à une autre coordonnée (supposée être le centre de la fente)
# ~ ... et ça marche !
# ~ F. Cochard

# Basic stuff
import logging
import random
import sys
import time

# Local stuff
from helper.IndiClient import IndiClient
from Mount.IndiMount import IndiMount

#Astropy stuff
from astropy import units as u
from astropy.coordinates import SkyCoord

# Astorpy helpers
import astropy.units as u

# Local code
from Guider import GuiderPHD2

# test indi client
indi_config = {
    "indi_host": "192.168.144.32",
    "indi_port": 7624
}
indi_cli = IndiClient(config=indi_config)

# Build the Mount
mount_config = {
    "mount_name":"10micron",
    # ~ "mount_name": "Telescope Simulator",
    "indi_client": indi_config
}
print("Je démarre...")
mount = IndiMount(config=mount_config)

# Get Pier side, not supported by simulator
# ~ ps = mount.get_pier_side()

# Unpark if you want something useful to actually happen
mount.unpark()
print(f"Status of the mount for parking is {mount.is_parked}")


# ~ c = SkyCoord(ra=ra*u.hourangle, dec=dec*u.degree, frame='icrs')
# ~ Cor Carolis : J2000 :	12h 56m 02s	 38° 19' 06"
# ~ c = SkyCoord("12h56m02s	 +38d19m06s", frame='icrs')
# ~ Deneb : J2000 :	20h 41m 25.91s	 45° 16' 49.19"
c = SkyCoord("20h41m25.91s	 +45d16m49.19s", frame='icrs')
print("BEFORE SLEWING --------------------------")
c_true = mount.get_current_coordinates()
print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")
mount.slew_to_coord_and_track(c)
print("After SLEWING --------------------------")
c_true = mount.get_current_coordinates()
print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")
print("Le télescope est maintenant sur la cible")

# Pour enviyer les messages de debug à la console (très verbeux)
#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s') 

config = {
    # ~ "host": "localhost",
    "host": "192.168.144.32",
    "port": 4400,
    "do_calibration": False,
    # ~ "profile_name": "Simulator",
    "profile_name": "St-Pancrasse",
    "exposure_time_sec": 0.1,
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
# ~ print(f"Is server connected: {g.is_server_connected()}")
g.connect_profile()
print(f"Is profile connected: {g.is_profile_connected()} = {g.is_profile_connected(g.profile_name)}")
print(f"Currently connected equipment is {g.get_current_equipment()}")
print("On passe le temps de pose à 0,5s")
g.set_exposure(0.1)
print("On démarre les images en boucle")
g.loop()

# Coordonnées de la position de l'étoile dans l'image (à estimer sur la base de l'astrométrie)
# ~ X = 649
# ~ Y = 517
# ~ Box_X = 50
# ~ Box_Y = 50
X = 1016 #int(1936/2)
Y = 777 # int(1216/2)
Box_X = 200
Box_Y = 200
# ~ RefX = X - (Box_X / 2)
# ~ RefY = Y - (Box_Y / 2)
# ret = g.find_star(x=946, y=690, width=200, height=200)
print(f"Run star selection : {X}, {Y}, avec {Box_X}, {Box_Y}")
ret = g.find_star(x=X, y=Y, width=Box_X, height=Box_Y)
# ~ g.find_star(649, 517, 100, 100)
print(f"=======> Return from find_star is {ret}")

# If successful, there should be a lock position set
# ~ ret = g.get_lock_position()
# ~ print(f"=======> Get lock position now returns {ret}")

LockX = 926.0
LockY = 683.0
g.set_lock_position(LockX, LockY, exact=True, wait_reached=False, angle_sep_reached=2*u.arcsec)
print(f"ooooooooooooo > nouvelle position {ret}")
time.sleep(1)

ret = g.get_lock_position()
print(f"Get lock position now returns {ret}")

ret = g.get_calibrated()
print(f"=======> Get Calibrated returns {ret}")

g.guide(recalibrate=False)
print(f"=======> Guiding is now steady, about to check lock position")

# guide for some time (receive takes some time)
# ~ for i in range(1*60):
    # ~ g.receive()
    # ~ time.sleep(1)

# you can use set_paused in full mode (pause both looping and guiding) to test if profile disconnection works
# ~ g.set_paused(paused=True, full="full")
# you can use set_paused without full mode (looping continues, but not guiding output)

# ~ print("Before disconnecting profile")
# ~ g.disconnect_profile()
# ~ print(f"Is profile connected: {g.is_profile_connected()} = {g.is_profile_connected(g.profile_name)}")
# ~ g.disconnect_server()
# ~ print(f"Is server connected: {g.is_server_connected()}")
# ~ g.terminate_server()
