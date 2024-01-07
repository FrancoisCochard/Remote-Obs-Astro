#!/usr/bin/python3

#-------------------------------------------------------------
# IPX800-V4.py
# Script to control the IPX800 (RelayBox)
# Version 0.01 - F. Cochard - 30 Dec 2023
#-------------------------------------------------------------

import requests
import yaml
import time
import subprocess

def ReadIPX800Config(Fichier):
    with open(Fichier, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data

Fichier = 'IPX800_V4/IPX800_config.yaml'
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
    # Test du 06/01/2024... raté. Je dois revoir en profondeur comment marche le système de log dans l'appli
    # logger.debug(f"Test de message...")

    
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
    url_indi_server = "http://192.168.144.32:8624/api/server/status"
    for i in range(25):
        time.sleep(2)
        try:
            r = requests.get(url_indi_server, timeout=2, verify=True)
            if r.status_code == 200 :
                break
        except requests.exceptions.Timeout:
            print("raté pour le moment... ", i)
        except requests.exceptions.ConnectionError as conerr: 
            print("Connection error", i)
    print("A la fin : ", r.text)
    result = r.json()
    print("Serveur status : ", result[0])
    FFF = result[0]
    for key in FFF:
        print(key,":", FFF[key])


def StopAllPSU():
    print("On démarre la séquence de mise hors tension")

    # Run the bash command to shutdown the Indi server
    # Few words about the Indi server Shutdown.
    # It is required to stop the server before shutting down the power supply.
    # We've defined a bash script to do the job. It is called indishutdown.
    # It is in the /usr/sbin/ directory.
    # Since the shutdown command requires the sudo password, I've updated the /etc/sudoers file, to allow the command without sudo.
    # And I've setup the ssh key to the client, to make sure the ssh command itself does not require the password.
    # ... it works!

    # result = subprocess.run("indishutdown", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.run("indishutdown")
    # print("Resultat du shutdown : ", result.stderr)
    time.sleep(5)
    print("Indi server (Raspberry Pi) shutdown done")
    
    StopMount()
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
    time.sleep(3)

    StopRaspiIndiServer()
    time.sleep(0.5)

    print("Ok, séquence terminée")
