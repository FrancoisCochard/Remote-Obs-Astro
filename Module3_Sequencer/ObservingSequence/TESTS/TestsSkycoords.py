from astropy.coordinates import SkyCoord
from astropy.coordinates import FK5

def target():
    vega =  SkyCoord("18h36m56s +38d47m1s", frame="icrs")
    return vega

# vega.dec.hms
# vega.transform_to('fk5')
# vega.transform_to(FK5(equinox='J2025'))
