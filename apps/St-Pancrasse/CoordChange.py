from astropy import units as u
from astropy.coordinates import SkyCoord
# c = SkyCoord(ra=10.625*u.degree, dec=41.2*u.degree, frame='icrs')

offset_long = 0.0
offset_lat = 2.0
print(f"Offset : long = {offset_long}, lat = {offset_lat}")

c_pole = SkyCoord(0.0*u.deg, 89.0*u.deg, frame='icrs')
print(f"coordonées objet (pole) : {c_pole}")
print(f"coordonées à pointer : {c_pole.spherical_offsets_by(offset_long*u.deg, offset_lat*u.deg)}")


offset_long = 2.0
offset_lat = 2.0
print(f"Offset : long = {offset_long}, lat = {offset_lat}")

c_equateur = SkyCoord(0.0*u.deg, 0.0*u.deg, frame='icrs')
print(f"coordonées objet  (équateur): {c_equateur}")
print(f"coordonées à pointer : {c_equateur.spherical_offsets_by(offset_long*u.deg, offset_lat*u.deg)}")

print(f"coordonées objet : {c_pole}")
print(f"coordonées à pointer (pole) : {c_pole.spherical_offsets_by(offset_long*u.deg, offset_lat*u.deg)}")

