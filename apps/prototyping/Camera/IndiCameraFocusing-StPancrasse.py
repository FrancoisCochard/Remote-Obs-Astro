# Basic stuff
import logging
import logging.config
import threading

# Miscellaneous
from astropy.io import fits
import io
import matplotlib.pyplot as plt
import numpy as np

# Local stuff : Camera
from Camera.IndiCamera import IndiCamera

# For this t
if __name__ == '__main__':

    # load the logging configuration
    logging.config.fileConfig('logging.ini')

    config = dict(
        camera_name='ZWO CCD ASI174MM Mini',
        autofocus_seconds=5,
        pointing_seconds=10,
        autofocus_size=504,
        autofocus_merit_function='half_flux_radius', #vollath_F4
        do_filter_wheel=False,
        focuser=dict(
            module="IndiFocuser",
            focuser_name="FocusLynx F1",
            port="/dev/serial/by-id/usb-Optec__Inc._Optec_USB_Serial_Cable_OP5AORA9-if00-port0",
            focus_range=dict(
                min=11000,
                max=13000),
            autofocus_step=dict(
                coarse=100,
                fine=300),
            autofocus_range=dict(
                coarse=4000,
                fine=4000),
            indi_client=dict(
                indi_host="192.168.144.32",
                indi_port="7624")
            ),
        indi_client=dict(
            indi_host="192.168.144.32",
            indi_port="7624")
        )

    # test indi virtual camera class
    cam = IndiCamera(config=config, connect_on_create=True)
    cam.prepare_shoot()

    def get_thumb(cam):
        thumbnail_size = 500
        cam.prepare_shoot()
        fits = cam.get_thumbnail(exp_time_sec=5, thumbnail_size=thumbnail_size)
        try:
            image = fits.data
        except:
            image = fits[0].data
        plt.imshow(image)
        plt.show()

    # Now focus
    assert(cam.focuser.is_connected)
    #autofocus_event = cam.autofocus_async(coarse=True)
    autofocus_event = cam.autofocus_async(coarse=False)
    autofocus_event.wait()
    print("Done")
