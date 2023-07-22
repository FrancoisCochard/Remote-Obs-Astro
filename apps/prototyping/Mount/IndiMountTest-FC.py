# Basic stuff
import logging
import random
import sys

# Local stuff
from helper.IndiClient import IndiClient
from Mount.IndiMount import IndiMount

#Astropy stuff
from astropy import units as u
from astropy.coordinates import SkyCoord

# test indi client
indi_config = {
    "indi_host": "192.168.144.32",
    "indi_port": 7624
}
indi_cli = IndiClient(config=indi_config)

# Build the Mount
mount_config = {
    # ~ "mount_name":"10micron",
    "mount_name": "Telescope Simulator",
    "indi_client": indi_config
}
mount = IndiMount(config=mount_config)

# Get Pier side, not supported by simulator
# ~ ps = mount.get_pier_side()

# Unpark if you want something useful to actually happen
mount.unpark()
print(f"Status of the mount for parking is {mount.is_parked}")


# ~ c = SkyCoord(ra=ra*u.hourangle, dec=dec*u.degree, frame='icrs')
# ~ Cor Carolis : J2000 :	12h 56m 02s	 38° 19' 06"
c = SkyCoord("12h56m02s	 +38d19m06s", frame='icrs')
print("BEFORE SLEWING --------------------------")
c_true = mount.get_current_coordinates()
print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")
mount.slew_to_coord_and_track(c)
print("After SLEWING --------------------------")
c_true = mount.get_current_coordinates()
print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")
print("Le télescope est maintenant sur la cible")

