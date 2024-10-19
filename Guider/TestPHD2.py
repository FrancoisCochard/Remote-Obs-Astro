#!/usr/bin/python3

# --------------------------------------
# Quick script to test the PHD2 server
# F. Cochard - Jan 2024
# 
# Status 28/01/2024
# - NNNNN Connexion OK
# - NNNNN All methods OK, tested on EFW (Zwo)
# --------------------------------------

from utils.LoggingUtils import initLogger
from Guider.GuiderPHD2 import GuiderPHD2 as toto
import yaml
import time

logger = initLogger('obs')

def ReadConfig(Fichier):
    with open(Fichier, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data

config = ReadConfig("Guider/PHD2_config.yaml")
print("J'ai lu la config : ", config)

A = toto(config=config, logger=logger)

print("Status : ", A.status())
# print("Connecté ?? ", A.get_connected())
A.connect_server()
print("Status après connect_server: ", A.status())
time.sleep(1)
A.connect_profile()
print("Status après connect_profile : ", A.status())

print("Status au moment de lancer le guide_from_to: ", A.status())
A.guide_from_to(951, 688, exact=True, settle=config['settle'], recalibrate=False, roi=[790, 893, 35, 35])
print("Status après le guide_from_to: ", A.status())

A.disconnect_profile()
A.disconnect_server()