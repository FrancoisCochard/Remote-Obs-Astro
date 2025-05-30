#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
Basic script for INDI mount Control.
C'est un outil de debug, pour apprendre à bien discuter avec le serveur INDI
- Original Version : F. Cochard - April 2025
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
"""

# ----------------------------------------------------------------------------------
# Loading libraries
# ----------------------------------------------------------------------------------

import cmd  # for command line instructions
from threading import Lock  # to manage multi-threading
import time  # gère le timing (for the function sleep)
# import serial  # Manages the serial port
# import serial.tools.list_ports  # Manages the serial ports list
from utils.LoggingUtils import initLogger
import Sequence as sq
from astropy.coordinates import SkyCoord
from Imaging import fits as fits_utils # FC, 29/05/2025 pour récupérer la fonction solve-field
from Imaging.Image import Image
from Imaging import fits

logger = initLogger("obs")
# ----------------------------------------------------------------------------------------------
# Variables definition
# ----------------------------------------------------------------------------------------------
# constants
# TIMEOUT_VALUE = 3
# Locker = Lock()  # Allows to lock processes during variable writing
vega =  SkyCoord("18h36m56s +38d47m1s", frame="icrs")
vega =  SkyCoord("8h26m55.44s -03d59m26.41s", frame="icrs")

# ----------------------------------------------------------------------------------------------
# Functions definition
# ----------------------------------------------------------------------------------------------

# def format(str):
#     "Formate une commande RS232"
#     str2 = str.strip("\n")
#     cs = hex(checksum(str2))[2:].zfill(2).upper()  # 2: to remove \x, zfill for 2 car
#     return str2 + "*" + cs + "\n"


# def checksum(str):
#     cks = 0
#     stringByte = bytes(str, "utf-8")
#     for car in stringByte:
#         cks = cks ^ car
#     return cks

def hms_coord(SkyCoord):
    return SkyCoord.to_string(style="hmsdms", precision=1)

# Copier-coller de Imaging.py FC, 29/05/2025
# def solve_field(self, **kwargs):
#     """ Solve field and populate WCS information
#         If you use basic catalog for astrometry.net, it is J2K!
#     Args:
#         **kwargs (dict): Options to be passed to `get_solve_field`
#     """
#     if kwargs.get("use_header_position", False):
#         kwargs.update(dict(
#             ra=self.header_pointing.ra.value,
#             dec=self.header_pointing.dec.value,
#         ))
#         if "radius" not in kwargs:
#             kwargs["radius"] = 1
#     solve_info = fits_utils.get_solve_field(
#         self.fits_file,
#         config=self.config,
#         **kwargs)
#     self.wcs_file = solve_info['solved_fits_file']
#     self.get_wcs_pointing()

#     # Remove some fields
#     for header in ['COMMENT', 'HISTORY']:
#         try:
#             del solve_info[header]
#         except KeyError:
#             pass

#     return solve_info
# ----------------------------------------------------------------------------------------------
# End of functions definition
# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
# Command line class definition
# ----------------------------------------------------------------------------------------------


class OBS_CLI(cmd.Cmd):
    """This class offers a command line tool.
    Each method starting with 'do_' is a command available for the user"""

    intro = "Welcome to UVEX control system.\nType help or ? to list commands"
    prompt = "\n> "

    # User commands
    # ----------------------------------------------------------------------------------------------
    # 1 - Commands for the mount
    # ----------------------------------------------------------------------------------------------

    def do_bye(self, arg):
        """bye - to quit the shelter control program."""
        # if SerialPortAvailable == True:
        #     port_serie.close()
        print("End of the script.\nGood bye!")
        exit()

    def do_get_parking(self,arg):
        """Pour connaître si la monture est parquée ou non"""
        Mount = sq.ObsData["Devices"]["mount"]
        print(f"Monture : {Mount}")
        park = Mount.is_parked
        print(f"parking : {park}")

    def do_get_position(self,arg):
        """Pour connaître la position courante de la monture"""
        Mount = sq.ObsData["Devices"]["mount"]
        print(f"Monture : {Mount}")
        c_true = Mount.get_current_coordinates()
        # print(f"Position : {c_true.ra.hms}, {c_true.dec.dms}")
        print(f'Position : {c_true.to_string(style="hmsdms", precision=1)}') #  sep=":",
        # to_string(style="hmsdms", sep=":", precision=1)

    def do_set_position(self,arg):
        """Pour déplacer la monture"""
        Mount = sq.ObsData["Devices"]["mount"]
        # print(f"Monture : {Mount}")
        if len(arg.split()) == 0:  # NO argument is required
            # RA = arg.split(" ")[0]
            # DEC = arg.split(" ")[1]
            # TargetCoord = SkyCoord(RA, DEC, frame="icrs")
            TargetCoord =  SkyCoord("18h36m56s +38d47m1s", frame="icrs") # Vega !
            Mount.slew_to_coord_and_track(TargetCoord)
            time.sleep(3)
            c_true = Mount.get_current_coordinates()
            print(f"Nouvelle position : {c_true}")
        else:
            print("Requires no argument")

    def do_goto_vega(self,arg):
        """Pour aller sur Vega (ou étoile enregistrée en dur)"""
        if len(arg.split()) == 0:  # NO argument is required
            # print(f"Vega : {vega}")
            Mount = sq.ObsData["Devices"]["mount"]
            c_true = Mount.get_current_coordinates()
            print(f"Avant pointage : {hms_coord(c_true)}")
            # print(f"Monture : {Mount}")
            print(f"Cible : {hms_coord(vega)}")
            sq.hilev.QuickPointing(Mount, vega)
            print("Le télescope est maintenant sur la cible")
            c_true = Mount.get_current_coordinates()
            print(f"Après pointage : {hms_coord(c_true)}")
        else:
            print("Requires no argument")

    def do_image_science(self,arg):
        """Faire une série d'images science"""
        if len(arg.split()) == 2:  # 2 argument are required
            nb = int(arg.split(" ")[0])
            exptime = int(arg.split(" ")[1])
            camera = sq.ObsData["Devices"]["science_camera"]
            image_name = sq.hilev.TakeScienceImage(camera, nb, exptime, Name='TEST')
            print(f"Image(s) enregistrée(s) sous : {image_name} ({nb} image(s) de {exptime} sec)")
        else:
            print("Requires 2 arguments (nb and exposure time)")
    
    def do_image_guidage(self,arg):
        """Faire une images guidage"""
        if len(arg.split()) == 1:  # 1 argument is required
            exptime = int(arg.split(" ")[0])
            camera = sq.ObsData["Devices"]["guiding_camera"]
            image_name = sq.hilev.TakeNoScienceImage(camera, exptime)
            print(f"Image enregistrée sous : {image_name} ({exptime} sec)")
        else:
            print("Requires 1 argument (exposure time)")
    
    def do_image_ambiance(self,arg):
        """Faire une images d'ambiance"""
        if len(arg.split()) == 1:  # 1 argument is required
            exptime = int(arg.split(" ")[0])
            camera = sq.ObsData["Devices"]["ambiance_camera"]
            image_name = sq.hilev.TakeNoScienceImage(camera, exptime)
            print(f"Image enregistrée sous : {image_name} ({exptime} sec)")
        else:
            print("Requires 1 argument (exposure time)")
 
    def do_image_pointage(self,arg):
        """Faire une images de pointage"""
        if len(arg.split()) == 1:  # 1 argument is required
            exptime = int(arg.split(" ")[0])
            camera = sq.ObsData["Devices"]["pointing_camera"]
            image_name = sq.hilev.TakeNoScienceImage(camera, exptime)
            print(f"Image enregistrée sous : {image_name} ({exptime} sec)")
        else:
            print("Requires 1 argument (exposure time)")

    def do_solve_image(self,arg):
        """Faire une astrométrie sur une image"""
        if len(arg.split()) == 0:  # 1 argument is required
            # exptime = int(arg.split(" ")[0])
            image = "/home/observatoire/TEST-solve/HD133131.fits"
            FitsImage = Image(image)
            # CenterCoord = FitsImage.solve_field()
            options = [
            '--no-verify',
            '--crpix-center',
            '--match', 'none',
            '--corr', 'none',
            # '--wcs', 'yes',
            ]
            fits.solve_field(image, solve_opts=options, verbose=True)
            print(f"Coordonnées du centre de l'image : {image}")
        else:
            print("Requires no argument... for the moment") 

# ----------------------------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------------------------


sq.StartAllPSU()
configINDIdevices = sq.ReadYamlConfig("IndiDevices/device_config.yaml")
sq.CreatIndiDevices(configINDIdevices)
sq.ConnectDevices()

# Run the CMD loop (command line interpreter)
OBS_CLI().cmdloop()
