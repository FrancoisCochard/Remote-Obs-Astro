#!/usr/bin/python3

# -----------------------------------------
# 
#
#
#
#
#
#
# -----------------------------------------

import time
import datetime
import json
from astropy.coordinates import SkyCoord
from astropy.io import fits as F
from astropy.wcs import WCS
import os.path
from astropy import units as u
import Module3_Sequencer.ObservingSequence.Low_level_operations as lowlev  # lowlev means 'Low Level Operation', or a basic operation in an observing sequence.
from Module3_Sequencer.Solver import fits as fits_utils # FC, 29/05/2025 pour récupérer la fonction solve-field

# --------------------
# GENERAL functions
# --------------------

def CreateObservationFile(ObsData):
    obsfilename = "TEST"
    print(f"Create the observation file: {obsfilename}.yaml - wait 3s")
    time.sleep(3)
    return "OK"

def CreateImageFileName(TargetOrType='NoName', ExpTime=0.0):
    # UniqueDate = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    UniqueDate = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    ImageFileName = UniqueDate + '-' + TargetOrType + '-' + str(ExpTime) + 's'
    return ImageFileName    

# --------------------
# FOCUS functions
# --------------------

def CheckFocusing(ObsData):
    print("Check telescope focusing - wait 3s")
    time.sleep(3)
    return "OK"

# --------------------
# SLIT POSITION functions
# --------------------

def DefineSlitPosition(ObsData):
    print("Define slit position - wait 3s")
    time.sleep(3)
    x1 = 1000
    x2 = 1000
    y1 = 1000
    y2 = 1000
    X = (x1 + x2) / 2
    Y = (y1 + y2) / 2
    return "OK"  # [X, Y]

# --------------------
# AUTOGUIDING functions
# --------------------

def ActivateAutoguiding(ObsData):
    print("Activate autoguiding (PHD2) - wait 3s")
    time.sleep(3)
    return "OK"

def StopAutoguiding(ObsData):
    print("Stop autoguiding (PHD2) - wait 3s")
    time.sleep(3)
    return "OK"

# --------------------
# PLATE SOLVING functions
# --------------------

def PlateSolveImage(ObsData,Image):
    # This function returns the coordinates of the image center
    Image_center = fits_utils.get_solve_field(Image)
    print("SOLVE terminé")
    wcs_info = fits_utils.get_wcsinfo(Image, verbose=True)
    print(f"Coordonnées du centre de l'image : {wcs_info}")
    return "OK"

# --------------------
# TARGET POINTING functions
# --------------------

def QuickPointing(Mount, TargetCoord):
    # TargetCoord = SkyCoord(RA, DEC, frame="icrs")
    # print(f"Target : {TargetCoord}")
    lowlev.PointingTelescopeToCoord(Mount, TargetCoord)
    return "OK (from High Level)"

def PointingTelescope():
    """Fonction FC Nov. 2024.
    On part de l'hypothèse que le télescope est proche de la cible - pour être du bon côté du pilier.
    """
    print("Pointing the telescope (precise)")
    # On lit le fichier Observatoire
    fileObservatory = "ObservingSequence/ObservatoryParameters.json"
    print(f"Fichier OBS existe : {os.path.exists(fileObservatory)}")
    with open(fileObservatory, "r") as file:
        pass
        Observatory = json.load(file)
    print(f"Data Obs : {Observatory}")

    # On lit le fichier Target
    fileTarget = "ObservingSequence/CurrentObs/CurrentTarget.json"
    print(f"Fichier Target existe : {os.path.exists(fileTarget)}")
    with open(fileTarget, "r") as file:
        pass
        Target = json.load(file)
    print(f"Data Obs : {Target}")
    RA = Target["RA"]
    DEC = Target["DEC"]
    TargetCoord = SkyCoord(RA, DEC, frame="icrs")
    print(f"Coordonées à pointer : {TargetCoord}")

    # On pointe le télescope

    # On lit l'image de guidage... NON ? (ce dont on a besoin, c'est les RADEC, et on les connaît déjà)
    file = "ObservingSequence/CurrentObs/Guidage.fits"
    print(f"Fichier existe : {os.path.exists(file)}")
    hdr = F.getheader(file)
    RA = hdr["RA"]
    DEC = hdr["DEC"]
    print(f"RA : {RA}, DEC : {DEC}")
    CurrentCoordinates = SkyCoord(ra=RA * u.degree, dec=DEC * u.degree, frame="fk5")
    print(f"Sky Coord FK5 : {CurrentCoordinates.fk5}")
    # CurrentCoordinates = SkyCoord(ra=RA*u.degree, dec=DEC*u.degree, frame='icrs')
    print(f"Sky Coord ICRS : {CurrentCoordinates.icrs}")

    # On interroge le côté de la monture (Est / Ouest vs le pilier)
    PierSide = hdr["PIERSIDE"]
    print(f"Pier side : {PierSide}")

    # On établit la position du centre de la fente (à partir du fichier observatoire)
    SlitX = Observatory["SlitX"]
    SlitY = Observatory["SlitY"]
    Scale = Observatory["pixelScale-arcsec"]
    CenterX = (hdr["NAXIS1"] - 1) / 2
    CenterY = (hdr["NAXIS2"] - 1) / 2
    print(f"Slit : {SlitX}, {SlitY}")

    # On calcule la position cible pour mettre l'étoile dans la fente
    if PierSide == "WEST":
        CorrectedRA = RA + (SlitX - CenterX) * Scale
        CorrectedDEC = DEC + (SlitY - CenterY) * Scale

    Iteration = 0
    PointingOK = False
    while PointingOK == False and Iteration < 3:
        # On pointe le télescope

        # On fait une image de guidage

        # On fait la mesure astrométrique
        file = "ObservingSequence/CurrentObs/Guidage.fits"
        # f = F.open(file)
        hdr = F.getheader(file)
        RA = hdr["RA"]
        DEC = hdr["DEC"]
        Command = (
            "solve-field --overwrite  --no-plots --new-fits none --ra "
            + str(RA)
            + " --dec "
            + str(DEC)
            + " --radius 1.0 "
            + file
        )
        print(f"Commande : {Command}")
        Resultat = os.system(Command)
        print(f"Res: {Resultat}")

        # On mesure l'écart de pointage (+ log)
        file = "ObservingSequence/CurrentObs/Guidage.new"
        print(f"WCS Fichier existe : {os.path.exists(file)}")
        hdr = F.getheader(file)
        w = WCS(hdr)
        CenterX = (hdr["NAXIS1"] - 1) / 2
        CenterY = (hdr["NAXIS2"] - 1) / 2
        RealCoordinates = w.pixel_to_world(CenterX, CenterY)
        print(f"SKY : {RealCoordinates}")

        # Si
        Iteration += 1
        #    On calcule les nouvelles coordonnées
        pass
    if Iteration >= 3:
        print(f"Le pointage a échoué, trop d'itérations")
        pass
    if PointingOK == True:
        # Le pointage a réussi
        pass
    # time.sleep(3)
    return "OK"

# --------------------------
# Cameras functions
# --------------------------

def TakeScienceImage(camera, nb, Exptime, Name='NoName'):
    print("Acquisition Science - début")
    ImageName = CreateImageFileName(TargetOrType=Name, ExpTime=Exptime)
    nb = int(nb)
    Exptime = float(Exptime)
    if (nb > 1) :
        for i in range(nb):
            ImageNameSerie = ImageName + '-' + str(i + 1) + '.fits'
            # FC, 12/04/2025 : je bride la taille des images parce que la lib INDI n'aime pas la pleine image ASI183
            Err, FitsIm = lowlev.TakeImage(camera, Exptime, ROI={'X':0, 'Y':1336, 'WIDTH':5495, 'HEIGHT':1000}) 
            Impath = '/tmp/' + ImageNameSerie
            FitsIm.writeto(Impath, overwrite=True)
    else : # Only one image
        Err, FitsIm = lowlev.TakeImage(camera, Exptime, ROI={'X':0, 'Y':1336, 'WIDTH':5495, 'HEIGHT':1000}) 
        Impath = '/tmp/' + ImageName + '.fits'
        FitsIm.writeto(Impath, overwrite=True)
    return ImageName

def TakeNoScienceImage(camera, Exptime):
    print("Acquisition - début")
    Err, FitsIm = lowlev.TakeImage(camera, Exptime) 
    FitsIm.writeto("/tmp/OtherImage.fits", overwrite=True)
    print(f"Acquisition - fin, {Err}")
    return "/tmp/OtherImage.fits"

def SetupCamera(camera, Gain=100, Offset=20, Temperature=None):
    # This is to setup the camera parameters (specially for the Science)
    if (Temperature != None):
        lowlev.SetCameraTemperature(camera, Temperature)
    lowlev.SetGainAndOffset(camera, Gain, Offset)
    return "OK"

def StopCoolingCamera(camera):
    lowlev.StopCameraCooling(camera)
    return "OK"


# --------------------------
# Temporary functions
# Cette partie a vocation à disparaître !
# --------------------------

def F1(devices_list, ObsData):
    print("F1 - début")
    time.sleep(3)
    print("F1 - fin")
    return "OK"

def F3(devices_list, ObsData):
    print("F3 - début")
    time.sleep(3)
    print("F3 - fin")
    return "OK"


def F4(devices_list, ObsData):
    print("F4 - début")
    time.sleep(3)
    print("F4 - fin")
    return "OK"


def F5(devices_list, ObsData):
    print("F5 - début")
    time.sleep(3)
    print("F5 - fin")
    return "OK"

def test():
    print("Hello de High level...")