#!/usr/bin/python3

# -----------------------------------------
# Low_level_operations.py
# V 0.01 - Jan 7th, 2024 - F. Cochard
# V 0.02 - 06/04/2025 - F. Cochard je réorganise les fichiers pour la séquence d'observation
# This script contains the operations used by the Observing sequences. These are the elementary bricks of the observations.
#
#
#
#
#
#
# -----------------------------------------
import time
from astropy import units as u

# --------------------
# MOUNT functions
# --------------------

def PointingTelescopeToCoord(ObsData, TargetCoord):
    print("Pointing the telescope (raw) - wait 3s")
    print(f"Devices Telescope : {ObsData}")
    mount = ObsData["Devices"]["mount"]
    print(f"Hello : {mount}")
    # On lit le fichier Target
    # fileTarget = "ObservingSequence/CurrentObs/CurrentTarget.json"
    # print(f"Fichier Target existe : {os.path.exists(fileTarget)}")
    # with open(fileTarget, "r") as file:
    #     pass
    #     Target = json.load(file)
    # print(f"Data Obs : {Target}")
    # RA = Target["RA"]
    # DEC = Target["DEC"]
    # mount.unpark() # à confirmer...
    # mount.slew_to_coord_and_stop() # Je dois encore donner les coordonnées
    # time.sleep(3)
    # c = SkyCoord("12h56m02s	 +38d19m06s", frame='icrs') # vEGA ?
    # c = SkyCoord("01h13m43s	 +07d34m31s", frame="icrs")
    # TargetCoord = SkyCoord(RA, DEC, frame="icrs")
    print(f"Coordonées à pointer : {TargetCoord}")

    print("BEFORE SLEWING --------------------------")
    c_true = mount.get_current_coordinates()
    print(
        f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}"
    )
    mount.slew_to_coord_and_track(TargetCoord)
    print("After SLEWING --------------------------")
    c_true = mount.get_current_coordinates()
    print(
        f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}"
    )
    print("Le télescope est maintenant sur la cible")
    return "OK"

# --------------------
# CAMERAS functions
# --------------------

def TakeScienceImage(ObsData, image_name):
    print("Ho...")
    camID = ObsData["Devices"]["science_camera"]
    if camID.is_connected:
        print("Ca va ")
        camID.prepare_shoot()
        camID.setExpTimeSec(2)
        print("Je vais démarrer la pose")
        camID.shoot_async()
        print("J'ai lancé le shoot_async")
        camID.synchronize_with_image_reception()
        print("Terminé le synchronize")
        fitsIm = camID.get_received_image()
        print("Image reçue !")
        ImName = image_name or "TESTAEFFACER.fits"
        fitsIm.writeto(ImName, overwrite=True)
    else:
        print("Device pas connecté")
    return "OK"


def TakeTargetSpectraSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} images of {exptime} seconds - wait 3s")
    print("... en fait, je ne prends qu'une image pour le moment")
    print(ObsData["Devices"])
    # camera = ObsData["Devices"]["ambiance_camera"]
    # TakeImage(camera, "Ambiance.fits")
    TakeScienceImage(ObsData, "Ambiance.fits")
    # camera = ObsData["Devices"]["science_camera"]
    # TakeImage(camera, "Science.fits")
    # camera = ObsData["Devices"]["guiding_camera"]
    # TakeImage(camera, "Guiding.fits")
    # time.sleep(3)
    return "OK"

def TakeCalibSpectraSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} calib images of {exptime} seconds - wait 3s")
    time.sleep(3)
    return "OK"


def TakeFlatSpectraSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} flat images of {exptime} seconds - wait 3s")
    time.sleep(3)
    return "OK"


def TakeDarkSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} dark images of {exptime} seconds - wait 3s")
    time.sleep(3)
    return "OK"


def TakeBiasSeries(ObsData):
    nb = 3
    print(f"Take {nb} bias images - wait 3s")
    time.sleep(3)
    return "OK"


