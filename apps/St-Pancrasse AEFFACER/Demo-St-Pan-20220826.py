# Script de découverte F. Cochard - Aout 2022

# Basic stuff
import logging
import random
import sys
import time

# Local stuff
from helper.IndiClient import IndiClient
from Mount.Indi10micronMount import Indi10micronMount

#Astropy stuff
from astropy import units as u
from astropy.coordinates import SkyCoord
# from astropy.io import fits

# Viz stuff
import matplotlib.pyplot as plt
from skimage import img_as_float
from skimage import exposure

# Local stuff : Camera
from Camera.IndiZwoASI120Camera import IndiZwoASI120Camera
from Camera.IndiZwoASI174MiniCamera import IndiZwoASI174MiniCamera
from Camera.IndiZwoASI183ProCamera import IndiZwoASI183ProCamera

if __name__ == '__main__':
	
    print("Toto")

    # test indi client
    indi_config = {
        "indi_host": "192.168.144.32",
        #"indi_host": "localhost",
        "indi_port": 7624
    }

    indi_cli = IndiClient(config=indi_config)

    print("Toto2")

    # Build the Mount
    mount_config = {
        #"mount_name":"Losmandy Gemini"
        #"mount_name": "Telescope Simulator",
        "mount_name": "10micron",
        "indi_client": indi_config
    }
    
    mount = Indi10micronMount(config=mount_config)
    
    print(f"Monture connectée... {mount.is_connected}")

    print(f"Status of the mount for parking is {mount.is_parked}")
    
    print("Je déparke !")
    mount.unpark()
    

    # Get Pier side, not supported by simulator
    ps = mount.get_pier_side()
    print(f"Pier side is {ps}")

    # Check coordinates
    c_true = mount.get_current_coordinates()
    print("BEFORE SLEWING --------------------------")
    print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")
    ra = '22h50m43s'
    dec = '+85d26m49s'
    # ~ ra = 20.71898
    # ~ dec = 17.26499
    # ~ ra = 21.13
    # ~ dec = 18.20
    # c = SkyCoord(ra=ra*u.hourangle, dec=dec*u.degree, frame='icrs')
    c = SkyCoord(ra, dec, frame='icrs')
    print(c)
    print(c.to_string('hmsdms'))
    print(f"Nouvelle cible: ra:{c.ra.to(u.hourangle)}, dec:{c.dec.to(u.degree)}")
    print("SLEWING ---------------------------------")
    mount.slew_to_coord_and_track(c)
    print("After SLEWING --------------------------")
    print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")
    
    mount.set_track_mode('TRACK_SIDEREAL')
    tr = mount.get_track_mode()
    print(f"Tracking mode: {tr}")
    
    # ~ time.sleep(0.5)
    # ~ print("Stop !")
    # ~ mount.abort_motion()
    
    print("Je parke !")
    mount.park()
    print("Parking terminé")
    
    print(f"Status parking : {mount.is_parked}")

# Je passe aux caméras

# 1 - D'abord la caméra d'ambiance
    # ~ print("\n---> Caméra Ambiance")

    # ~ configAmbiance = dict(
        # ~ camera_name='ZWO CCD ASI120MM-S 1',
        # ~ autofocus_seconds=5,
        # ~ pointing_seconds=5,
        # ~ autofocus_size=500,
        # ~ indi_client = indi_config)

    # ~ # test indi virtual camera class
    # ~ camAmbiance = IndiZwoASI120Camera(config=configAmbiance, connect_on_create=False)
    # ~ camAmbiance.connect()
    # ~ print("ASI 120 Ambiance Connectée...")

    # ~ camAmbiance.set_roi({'X': 0, 'Y': 0, 'WIDTH': 1280, 'HEIGHT': 1024})
    # ~ # get_roi
    # ~ print(f"Current camera ROI is: {camAmbiance.get_roi()}")

    # ~ # set frame type (mostly for simulation purpose
    # ~ camAmbiance.set_frame_type('FRAME_LIGHT')
    # ~ print("Passé en frame Light")

    # ~ # set gain
    # ~ camAmbiance.set_gain(100)
    # ~ print(f"gain ambiance is {camAmbiance.get_gain()}")

    # ~ # Je passe en 16 bits
    # ~ camAmbiance.set_frame_depth(16)
    # ~ print(f"Depth ambiance is now {camAmbiance.get_frame_depth()}")
    
    # ~ # Acquire image Ambiance
    # ~ camAmbiance.prepare_shoot()
    # ~ camAmbiance.setExpTimeSec(0.001)
    # ~ camAmbiance.shoot_async()

# ~ # 2 - Ensuite la caméra de pointage
    # ~ print("\n---> Caméra Pointage")

    # ~ configPointage = dict(
        # ~ camera_name='ZWO CCD ASI120MM-S',
        # ~ autofocus_seconds=5,
        # ~ pointing_seconds=5,
        # ~ autofocus_size=500,
        # ~ indi_client = indi_config)

    # ~ # test indi virtual camera class
    # ~ camPointage = IndiZwoASI120Camera(config=configPointage, connect_on_create=False)
    # ~ camPointage.connect()
    # ~ print("ASI 120 Pointage Connectée...")

    # ~ camAmbiance.set_roi({'X': 0, 'Y': 0, 'WIDTH': 1280, 'HEIGHT': 1024})
    # ~ # get_roi
    # ~ print(f"Current camera ROI is: {camPointage.get_roi()}")

    # ~ # set frame type (mostly for simulation purpose
    # ~ camPointage.set_frame_type('FRAME_LIGHT')
    # ~ print("Passé en frame Light")

    # ~ # set gain
    # ~ camPointage.set_gain(100)
    # ~ print(f"gain pointage is {camPointage.get_gain()}")
    
    # ~ # Profondeur d'image
    # ~ print(f"Depth pointage is {camPointage.get_frame_depth()}")
    # ~ # Je passe en 16 bits
    # ~ camPointage.set_frame_depth(16)
    # ~ print(f"Depth pointage is now {camPointage.get_frame_depth()}")
    
    # ~ # Acquire image Pointage
    # ~ camPointage.prepare_shoot()
    # ~ camPointage.setExpTimeSec(0.01)
    # ~ camPointage.shoot_async()

# 3 - Puis la caméra de guidage
    print("\n---> Caméra Guidage")

    configGuidage = dict(
        camera_name='ZWO CCD ASI174MM Mini',
        autofocus_seconds=5,
        pointing_seconds=5,
        autofocus_size=500,
        indi_client = indi_config)

    # test indi virtual camera class
    camGuidage = IndiZwoASI174MiniCamera(config=configGuidage, connect_on_create=False)
    camGuidage.connect()
    print("Caméra de guidage Connectée...")

    # ~ camAmbiance.set_roi({'X': 0, 'Y': 0, 'WIDTH': 1280, 'HEIGHT': 1024})
    # ~ # get_roi
    # ~ print(f"Current camera ROI is: {camGuidage.get_roi()}")

    #print('Setting cooling on')
    #camAmbiance.set_cooling_on() THIS VECTOR IS EXPECTED TO BE IN BUSY STATE, NOT IDLE NOR OK, THAT's WHY THERE IS TIMEOUT
    # ~ print(f"Current camera temperature is: {camAmbiance.get_temperature()}")
    # ~ target_temp = -5.5
    # ~ print(f"Now, setting temperature to: {target_temp}")
    # ~ camAmbiance.set_temperature(target_temp)
    # ~ print(f"Current camera temperature is: {camAmbiance.get_temperature()}")
    # ~ target_temp = -8
    # ~ print(f"Now, setting temperature to: {target_temp}")
    # ~ camAmbiance.set_temperature(target_temp)
    # ~ print(f"Current camera temperature is: {camAmbiance.get_temperature()}")
    #camAmbiance.set_cooling_off()

    # set frame type (mostly for simulation purpose
    camGuidage.set_frame_type('FRAME_LIGHT')
    print("Passé en frame Light")

    # set gain
    camGuidage.set_gain(100)
    print(f"gain is {camGuidage.get_gain()}")
    
    # Profondeur d'image
    print(f"Depth is {camGuidage.get_frame_depth()}")
    # Je passe en 16 bits
    # camGuidage.set_frame_depth(16)
    camGuidage.set_frame_depth(8)
    print(f"Depth is now {camGuidage.get_frame_depth()}")
    
    # Acquire image Guidage
    camGuidage.prepare_shoot()
    camGuidage.setExpTimeSec(10.0)
    camGuidage.shoot_async()


# ~ # 4 - Enfin la caméra Science
    # ~ print("\n---> Caméra Science")

    # ~ configScience = dict(
        # ~ camera_name='ZWO CCD ASI183MM Pro',
        # ~ autofocus_seconds=5,
        # ~ pointing_seconds=5,
        # ~ autofocus_size=500,
        # ~ indi_client = indi_config)

    # ~ # test indi virtual camera class
    # ~ camScience = IndiZwoASI183ProCamera(config=configScience, connect_on_create=False)
    # ~ camScience.connect()
    # ~ print("Caméra science Connectée...")

    # ~ camAmbiance.set_roi({'X': 0, 'Y': 0, 'WIDTH': 1280, 'HEIGHT': 1024})
    # ~ # get_roi
    # ~ print(f"Current camera ROI is: {camScience.get_roi()}")

    #print('Setting cooling on')
    #camAmbiance.set_cooling_on() THIS VECTOR IS EXPECTED TO BE IN BUSY STATE, NOT IDLE NOR OK, THAT's WHY THERE IS TIMEOUT
    # ~ print(f"Current camera temperature is: {camAmbiance.get_temperature()}")
    # ~ target_temp = -5.5
    # ~ print(f"Now, setting temperature to: {target_temp}")
    # ~ camAmbiance.set_temperature(target_temp)
    # ~ print(f"Current camera temperature is: {camScience.get_temperature()}")
    # ~ target_temp = -8
    # ~ print(f"Now, setting temperature to: {target_temp}")
    # ~ camAmbiance.set_temperature(target_temp)
    # ~ print(f"Current camera temperature is: {camAmbiance.get_temperature()}")
    #camAmbiance.set_cooling_off()

    # ~ # set frame type (mostly for simulation purpose
    # ~ camScience.set_frame_type('FRAME_LIGHT')
    # ~ print("Passé en frame Light")

    # ~ # set gain
    # ~ camScience.set_gain(100)
    # ~ print(f"gain is {camScience.get_gain()}")
    
    # ~ # Profondeur d'image
    # ~ print(f"Depth is {camScience.get_frame_depth()}")
    # ~ # Je passe en 16 bits
    # ~ camScience.set_frame_depth(16)
    # ~ print(f"Depth is now {camScience.get_frame_depth()}")
    
    # ~ # Acquire image Guidage
    # ~ camScience.prepare_shoot()
    # ~ camScience.setExpTimeSec(15)
    # ~ camScience.shoot_async()

    # ~ camAmbiance.synchronize_with_image_reception()
    # ~ fitsAmbiance = camAmbiance.get_received_image()
    # ~ camPointage.synchronize_with_image_reception()
    # ~ fitsPointage = camPointage.get_received_image()
    camGuidage.synchronize_with_image_reception()
    fitsGuidage = camGuidage.get_received_image()
    fitsGuidage.writeto('new1.fits')

    # hdu = fits.PrimaryHDU(n)
    # fitsGuidage.
    # ~ camScience.synchronize_with_image_reception()
    # ~ fitsScience = camScience.get_received_image()


    # Show images
    # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(16, 9))
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(16, 9))

    # ~ imgAmb = fitsAmbiance[0].data
    # ~ img_eqAmb = exposure.equalize_hist(imgAmb)
    # ~ print_ready_imgAmb = img_as_float(img_eqAmb)
    # ~ # print(f"Print ready has shape {print_ready_img.shape}")
    # ~ ax1.imshow(print_ready_imgAmb, cmap='gray')
    
    # ~ imgPoint = fitsPointage[0].data
    # ~ img_eqPoint = exposure.equalize_hist(imgPoint)
    # ~ print_ready_imgPoint = img_as_float(img_eqPoint)
    # ~ ax2.imshow(print_ready_imgPoint, cmap='gray')
    
    imgGuide = fitsGuidage[0].data
    img_eqGuide = exposure.equalize_hist(imgGuide)
    print_ready_imgGuide = img_as_float(img_eqGuide)
    ax3.imshow(print_ready_imgGuide, cmap='gray')

    # ~ imgScience = fitsScience[0].data
    # ~ img_eqScience = exposure.equalize_hist(imgScience)
    # ~ print_ready_imgScience = img_as_float(img_eqScience)
    # ~ ax4.imshow(print_ready_imgScience, cmap='gray')

    plt.show()
