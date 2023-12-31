#!/usr/bin/python3

#-------------------------------------------------------------
# IPX800-V4.py
# Script to control the IPX800 (RelayBox)
# Version 0.01 - F. Cochard - 30 Dec 2023
#-------------------------------------------------------------

import requests
import yaml
import time

def ReadIPX800Config(Fichier):
    with open(Fichier, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data

Fichier = 'IPX800-V4/IPX800_config.yaml'
config_data = ReadIPX800Config(Fichier)

url_base = "http://" + config_data['IPX800_host'] + "/api/xdevices.json?key=apikey&"

def StartMount():
    url = url_base + "Set" + config_data['IO']['Mount_OnOff']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopMount():
    url = url_base + "Clear" + config_data['IO']['Mount_OnOff']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartGeneral12V():
    url = url_base + "Set" + config_data['IO']['General_12V']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopGeneral12V():
    url = url_base + "Clear" + config_data['IO']['General_12V']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartUSB3Hub():
    url = url_base + "Set" + config_data['IO']['USB3_Hub']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopUSB3Hub():
    url = url_base + "Clear" + config_data['IO']['USB3_Hub']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartScienceCamera():
    url = url_base + "Set" + config_data['IO']['Science_Cam']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopScienceCamera():
    url = url_base + "Clear" + config_data['IO']['Science_Cam']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartFocuser():
    url = url_base + "Set" + config_data['IO']['Focuser']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopFocuser():
    url = url_base + "Clear" + config_data['IO']['Focuser']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartSPOX():
    url = url_base + "Set" + config_data['IO']['SPOX']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopSPOX():
    url = url_base + "Clear" + config_data['IO']['SPOX']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartRaspiIndiServer():
    url = url_base + "Set" + config_data['IO']['RasPi4_Indi']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StopRaspiIndiServer():
    url = url_base + "Clear" + config_data['IO']['RasPi4_Indi']
    r = requests.get(url)
    result = r.json()
    return result['status']

def StartAllPSU():
    print("On démarre la séquence de mise sous tension")
    
    StartMount()
    time.sleep(0.5)

    StartRaspiIndiServer()
    time.sleep(0.5)

    StartGeneral12V()
    time.sleep(0.5)

    StartUSB3Hub()
    time.sleep(0.5)

    StartScienceCamera()
    time.sleep(0.5)

    StartFocuser()
    time.sleep(0.5)

    StartSPOX()
    time.sleep(0.5)

    print("Ok, séquence terminée")

def StopAllPSU():
    print("On démarre la séquence de mise hors tension")
    
    StopMount()
    time.sleep(0.5)

    StopRaspiIndiServer()
    time.sleep(0.5)

    StopGeneral12V()
    time.sleep(0.5)

    StopUSB3Hub()
    time.sleep(0.5)

    StopScienceCamera()
    time.sleep(0.5)

    StopFocuser()
    time.sleep(0.5)

    StopSPOX()
    time.sleep(0.5)

    print("Ok, séquence terminée")


StartAllPSU()
time.sleep(5)
StopAllPSU()