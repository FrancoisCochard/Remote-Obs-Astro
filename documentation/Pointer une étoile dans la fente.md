# Pointer une étoile dans la fente par astrométrie

| Version | Date       | Qui        | Quoi             |
| ------- | ---------- | ---------- | ---------------- |
| 0.01    | 01/12/2024 | F. Cochard | Première ébauche |
|         |            |            |                  |
|         |            |            |                  |

## Introduction

Dans le cadre de l'observation automatique (et robotique), le système doit être capable de placer l'étoile cible dans la fente du spectro, en tenant compte de l'erreur de pointage du télescope ainsi que de la position de la fente dans l'image (elle n'est jamais exactement au centre de l'image). 

Cela est rendu possible (et simple) grâce à deux éléments :

- Les outils de résolution astrométrique (dans notre cas **Astrometry.net**), utilisé localement sous Linux,
- La librairie **Astropy** (en **Python**) qui propose un outil puissant de système de coordonnées **SysCoord** (coordonnées RA-DEC), avec des fonctions de conversion (entre pixels et coordonnées sur le ciel) et de calculs de décalages (offset). 

Ce document propose une méthode directe (par opposition à une méthode itérative) de pointage du télescope.

On considère que l'on travaille avec une monture allemande (qui doit faire un retournement au méridien) de qualité (peu de jeu), et mise en station (même approximativement).

## Principe général

La méthode consiste à pointer une première fois le télescope aux coordonnées théoriques de la cible, puis de faire une image de guidage, et d'en calculer les coordonnées RA-DEC du centre par résolution astrométrique.

Cette première image va permettre de mesurer l'erreur de pointage, ainsi que de définir la position de la monture par rapport au pilier (dans le cas d'une monture allemande qui doit faire un retournement au méridien). On fera l'hypothèse que la monture restera du même côté du pilier par la suite (en pratique, ce point sera à vérifier). Note : le retournement de monture conduit à une inversion de l'écart des coordonnées sur le ciel de la position de la fente par rapport au centre de l'image.

On indiquera par ailleurs la position du centre de la fente dans cette image de guidage (en pixels X et Y).

On pourra alors calculer de nouvelles coordonnées à donner au télescope pour que l'étoile se place dans la fente. En théorie une seule itération est suffisante, mais en pratique on pourra préférer une méthode par itérations, pour garantir une précision de pointage.

## Définitions

On a besoin d'utiliser plusieurs coordonnées pour faire le calcul. On suppose ici que le système de coordonnées est le même dans toute la procédure (J2000 ou Jnow, ICRS ou FK5). Note : quand on fait un pointage de précision - c'est notre cas ici - la différence de coordonnées entre J2000 et Jnow (ou d'autres encore) est clairement visible. Il sera impossible de mettre l'étoile dans la fente si on mélange ces systèmes. 

- Coordonnées de la **cible** (RA-DEC) : c'est la position de l'étoile que l'on trouve dans les catalogues. L'objectif de la méthode est de confondre ces coordonnées avec celles de la fente sur le ciel.
- Coordonnées du **télescope** (RA-DEC) : ce sont les coordonnées que l'on donne au télescope lors d'un ordre de pointage. Ce sont également les coordonnées indiquées par le même télescope si on l'interroge sur sa position.
- Coordonnées du **centre de l'image** (RA-DEC) : ce sont les coordonnées calculées par la résolution astrométrique.
- Coordonnées de la **fente** (pixel X,Y) : ce sont les coordonnées du centre de la fente dans l'image. Elles doivent être indiquées "manuellement" (cela peut aussi faire l'objet d'un calcul automatique, mais ce n'est pas l'objet de ce document).

A partir de ces différentes coordonnées, on peut définir quelques valeurs importantes :

- L'**erreur de pointage**, qui est la distance (en delta-RA et delta-DEC) entre les coordonnées du centre de l'image et celles du télescope.
- Le **décalage de la fente** correspond à la distance en pixels entre le centre de la fente et le centre de l'image.

## Méthode

On commence par pointer le télescope aux coordonnées (catalogue) de la cible. Puis on fait une image (caméra de guidage), dont on calcule la résolution astrométrique. L'image est alors complétée par les données WCS qui permettent de calculer la position sur le ciel de n'importe quel pixel. 

On peut alors calculer les coordonnées sur le ciel du centre de l'image :

```python
from astropy.io import fits as F
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

Image = "Image_Guidage.fits"
hdr = F.getheader(Image)
w = WCS(hdr)
ImageCenterX = (hdr["NAXIS1"] - 1) / 2 # l'image commence au pixel 0,0
ImageCenterY = (hdr["NAXIS2"] - 1) / 2
ImageCenterRADEC = w.pixel_to_world(ImageCenterX, ImageCenterY)
print(ImageCenterRADEC)
>>> <SkyCoord (FK5: equinox=2000.0): (ra, dec) in deg
    (42.54089868, 27.18865737)>
```

De la même manière, on calcule les coordonnées sur le ciel de la fente : 

```python
from astropy.io import fits as F
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

Image = "Image_Guidage.fits"
hdr = F.getheader(Image)
w = WCS(hdr)
SlitX = 850
SlitY = 495
SlitCenterRADEC = w.pixel_to_world(SlitX, SlitX)
print(SlitCenterRADEC)
>>> <SkyCoord (FK5: equinox=2000.0): (ra, dec) in deg
    (42.56771956, 27.13767234)>
```

**Note importante** : La position de la fente sur le ciel est directement dépendante du côté de la monture par rapport au pilier. Nous n'avons pas besoin de savoir ici de quel côté est la monture, parce que cette information est indirectement contenue dans l'image (au travers des paramètres WCS), mais si on pointait exactement le même champ avec la monture de l'autre côté, la position de la fente serait inversée par rapport au centre de l'image.

On dispose maintenant des 4 coordonnées dont on a besoin : la cible (catalogue), le télescope, le centre de l'image et la fente. 

Il nous reste à calculer l'erreur de pointage est le décalage de la fente. On pourrait imaginer qu'il s'agit de simples conversions X-Y vers des angles en prenant en compte l'échantillonnage de l'image (qui est également donné par la résolution astrométrique), mais c'est en fait plus complexe que cela. Non seulement parce que l'image est probablement légèrement (ou plus) tournée par rapport aux axes du ciel, mais en outre on est dans un système de coordonnées sphérique. Imaginez pour vous en convaincre que vous pointez très près du pôle... les coordonnées du télescope et celles du centre de l'image peuvent se trouver chacune d'un côté du pôle, et malgré la proximité physique de ces deux points (quelques arcminutes) leurs coordonnées peuvent être radicalement différentes !

La bonne nouvelle, c'est que la méthode rigoureuse n'est pas bien compliquée, grâce à la librairie Astropy.

L'erreur de pointage correspond aux deux angles (sur le ciel) delta-RA et delta-DEC que l'on peut calculer avec la fonction **spherical_offsets_to()** :

```python
import astropy.units as u
from astropy.coordinates import SkyCoord

TelescopeCoord = SkyCoord('8h50m59.75s', '+11d39m22.15s', frame='fk5')
ImageCenter = SkyCoord('8h50m47.92s', '+11d39m32.74s', frame='fk5')
draErreurPointage, ddecErreurPointage = TelescopeCoord.spherical_offsets_to(ImageCenter)
draErreurPointage.to(u.arcsec)  
>>> <Angle -173.78873354 arcsec>
ddecErreurPointage.to(u.arcsec)  
>>> <Angle 10.60510342 arcsec>
```

Notez que le système SkyCoord de Astropy permet d'innombrables conversions d'unités, c'est à la fois simple et très efficace. Prenez le temps de regarder la documentation (cf références ci-dessous)

De la même manière, le décalage de fente est un système de deux angles  calculées à partir des valeurs trouvées plus haut :

```python
import astropy.units as u
from astropy.coordinates import SkyCoord

draDecalageFente, ddecDecalageFente = ImageCenterRADEC.spherical_offsets_to(SlitCenterRADEC)
draDecalageFente
>>> <Angle -0.04827465 deg>
ddecDecalageFente
>>> <Angle 0.00294586 deg>
```

La suite est évidemment simple : on peut calculer de la même manière les nouvelles coordonnées à pointer par le télescope en prenant en compte l'erreur de pointage et le décalage de la fente : 

Nouvelles Coordonnées Télescope (RA-DEC) = Coordonnées cible (RA-DEC) - erreur de pointage (dRA-dDEC) - décalage de la fente (dRA-dDEC)

Cela se traduit en Python par les commandes suivantes, qui se basent sur la fonction **spherical_offsets_by()** , inverse de **spherical_offsets_to()** :

```python
import astropy.units as u
from astropy.coordinates import SkyCoord

TargetCoord = SkyCoord('8h50m59.75s', '+11d39m22.15s', frame='fk5') # (coordonnées catalogue)
# Correction de l'erreur de pointage :
NewImageCoord = TargetCoord.spherical_offsets_by(-draErreurPointage,-draErreurPointage)
# Puis correction du décalage de la fente :
NewTelescopeCoord = NewImageCoord.spherical_offsets_by(-draDecalageFente,-ddecDecalageFente)
NewTelescopeCoord
>>> <SkyCoord (FK5: equinox=J2000.000): (ra, dec) in deg
    (132.67530469, 11.65885539)>
```

Bien entendu, si on refait une image de contrôle avec cette nouvelle position (c'est fortement recommandé, bien sûr), le centre de l'image doit maintenant se trouver aux coordonnées de la cible auxquelles on ajoute le décalage de la fente. Si cette condition est remplie, alors on peut considérer que l'étoile est dans la fente.

**Note importante** : dans les exemples ci-dessus, je n'ai pas regardé dans le détail le signe des corrections. Il faut évidemment être très rigoureux sur ce point !

# Références

- Astrometry.net : 

- Astropy (séparations, offests etc) : https://docs.astropy.org/en/stable/coordinates/matchsep.html