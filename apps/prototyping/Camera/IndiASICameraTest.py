# Version modifiée FC à Arcueil, 25/12/2023... à utiliser pour les tests

# Viz stuff
# import matplotlib.pyplot as plt
# from skimage import img_as_float
# from skimage import exposure
from datetime import datetime

# Local stuff : Camera
from IndiDevices.Camera.IndiASICamera import IndiASICamera

if __name__ == '__main__':
    config = dict(
        camera_name='ZWO CCD ASI183MM Pro',
        indi_client=dict(
            indi_host="192.168.144.32",
            indi_port=7624),
    )

    # test indi virtual camera class
    cam = IndiASICamera(config=config, connect_on_create=False)
    print("Type initial cam : ", type(cam))
    cam.connect()

    # Play with camera configuration
    cam.set_roi({'X': 256, 'Y': 480, 'WIDTH': 512, 'HEIGHT': 640})
    # get_roi
    print(f"Current camera ROI is: {cam.get_roi()}")
    cam.set_roi({'X': 0, 'Y': 0, 'WIDTH': 1280, 'HEIGHT': 1024})
    # get_roi
    print(f"Current camera ROI is: {cam.get_roi()}")

    #print('Setting cooling on')
    #cam.set_cooling_on() THIS VECTOR IS EXPECTED TO BE IN BUSY STATE, NOT IDLE NOR OK, THAT's WHY THERE IS TIMEOUT
    print(f"Current camera temperature is: {cam.get_temperature()}")
    target_temp = 0
    print(f"Now, setting temperature to: {target_temp}")
    print(f"Current camera temperature is: {cam.get_temperature()}")

    # set frame type (mostly for simulation purpose
    cam.set_frame_type('FRAME_DARK')
    cam.set_frame_type('FRAME_FLAT')
    cam.set_frame_type('FRAME_BIAS')
    cam.set_frame_type('FRAME_LIGHT')

    # set gain
    print(f"gain is {cam.get_gain()}")
    cam.set_gain(100)
    print(f"gain is {cam.get_gain()}")

    # Acquire data
    Avant = datetime.now()
    cam.prepare_shoot()
    cam.setExpTimeSec(2)
    print("Je vais démarrer la pose", datetime.now())
    cam.shoot_async()
    print("J'ai lancé le shoot_async", datetime.now())
    cam.synchronize_with_image_reception()
    print("Terminé le synchronize", datetime.now())
    fitsIm = cam.get_received_image()
    print("Image reçue !", datetime.now())
    print(type(fitsIm))
    ImName = "TESTAEFFACER.fits"
    fitsIm.writeto(ImName, overwrite=True)
    Apres = datetime.now()
    duree = (Apres - Avant).total_seconds()
    ## On affiche le résultat
    print(f"durée de l'acquisition : {duree} secondes")

    # Show image
    # fig, ax = plt.subplots(1, figsize=(16, 9))
    # img = fits[0].data
    # img_eq = exposure.equalize_hist(img)
    # print_ready_img = img_as_float(img_eq)
    # print(f"Print ready has shape {print_ready_img.shape}")
    # ax.imshow(print_ready_img)
    # plt.show()
