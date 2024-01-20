#!/usr/bin/python3

# -----------------------------------------
# ObservingOperations.py
# V 0.01 - Jan 7th, 2024 - F. Cochard
# This script contains the operations used by the Observing sequences. These are the elementary bricks of the observations.
# 
# 
# 
# 
# 
# 
# -----------------------------------------
import time

def RawPointingTelescope(ObsData):
    print("Pointing the telescope (raw) - wait 3s")
    time.sleep(3)
    return 'OK'

def CheckFocusing(ObsData):
    print("Check telescope focusing - wait 3s")
    time.sleep(3)
    return 'OK'

def DefineSlitPosition(ObsData):
    print("Define slit position - wait 3s")
    time.sleep(3)
    x1 =1000
    x2 =1000
    y1 = 1000
    y2 = 1000
    X = (x1 + x2) / 2
    Y = (y1 + y2) / 2
    return 'OK' #[X, Y]

def PrecisePointingTelescope(ObsData):
    print("Pointing the telescope (precise) - wait 3s")
    time.sleep(3)
    return 'OK'

def ActivateAutoguiding(ObsData):
    print("Activate autoguiding (PHD2) - wait 3s")
    time.sleep(3)
    return 'OK'

def TakeTargetSpectraSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} images of {exptime} seconds - wait 3s")
    print("... en fait, je ne prends qu'une image pour le moment")
    print(ObsData['Devices'])
    camera = ObsData['Devices']['science_camera']
    # camera = ObsData['Devices']['ScienceCam']
    print("GFH ", camera)
    TakeImage(camera)
    time.sleep(3)
    return 'OK'

def StopAutoguiding(ObsData):
    print("Stop autoguiding (PHD2) - wait 3s")
    time.sleep(3)
    return 'OK'

def TakeCalibSpectraSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} calib images of {exptime} seconds - wait 3s")
    time.sleep(3)
    return 'OK'

def TakeFlatSpectraSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} flat images of {exptime} seconds - wait 3s")
    time.sleep(3)
    return 'OK'

def TakeDarkSeries(ObsData):
    nb = 3
    exptime = 2
    print(f"Take {nb} dark images of {exptime} seconds - wait 3s")
    time.sleep(3)
    return 'OK'

def TakeBiasSeries(ObsData):
    nb = 3
    print(f"Take {nb} bias images - wait 3s")
    time.sleep(3)
    return 'OK'

def CreateObservationFile(ObsData):
    obsfilename = "TEST"
    print(f"Create the observation file: {obsfilename}.yaml - wait 3s")
    time.sleep(3)
    return 'OK'

#--------------------------
# Temporary functions
#--------------------------

def TakeImage(science_cam):
    print("Ho...") #, science_cam)
    if science_cam.is_connected:
        # science_cam = devices_list[Science]
        science_cam.prepare_shoot()
        science_cam.setExpTimeSec(2)
        print("Je vais démarrer la pose")
        science_cam.shoot_async()
        print("J'ai lancé le shoot_async")
        science_cam.synchronize_with_image_reception()
        print("Terminé le synchronize")
        fitsIm = science_cam.get_received_image()
        print("Image reçue !")
        ImName = "TESTAEFFACER.fits"
        fitsIm.writeto(ImName, overwrite=True)
    else:
        print("Device pas connecté")

def F1(devices_list, ObsData):
    print("F1 - début")
    time.sleep(3)
    print("F1 - fin")
    return "OK"

def TakeOneImage(devices_list, ObsData):
    print("Acquisition - début")
    # time.sleep(3)
    camera = devices_list['ScienceCam']
    TakeImage(camera)
    print("Acquisition - fin")
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