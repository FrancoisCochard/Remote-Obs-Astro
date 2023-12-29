#!/usr/bin/env python3

"""
Le 01/10/2022, je bute sur deux petits problèmes :
- Les coordonnées détecteés dans l'image (HD133131) ne correspondent pas du tout à cet objet
- Le nom OBJECT enregstré dans le header de l'image n'est pas le bon
(HD 140436 au lieu de HD133131) ; et c'est le même objet indiqué pour tous les fichiers. Bug à l'acquisition.
La prochaine fois que je teste, je dois vérifier ces éléments (et si la zone pointée est la bonne à l'image)
La bonne nouvelle : les coordonnées WCS correspondent bien à l'image (si je me base sur Simbad et Aladin)
... et je note aussi au passage que la résolution astro a été très rapide, donc les coordonnées pointées 
devaient être bonnes.
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.coordinates import SkyCoord  # High-level coordinates
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
import astropy.units as u
from astropy.wcs import WCS

hdul = fits.open('GuidingField/HD151043.fits')
print(hdul.info())

image_data = hdul[0].data
hdr = hdul[0].header
print(hdr['OBJECT'])
# ~ print(type(image_data))
# ~ print(image_data.shape)

w = WCS(hdul[0].header)
print('WCS : ', w)
sky = w.pixel_to_world(1067, 593)
print("type : ", type(sky))
print(sky.to_string('hmsdms'))  

# image_data = fits.getdata(image_file)

plt.imshow(image_data, cmap='gray', vmin=0, vmax=1000)
plt.colorbar()
plt.show()

hdul.close()
