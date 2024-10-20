#!/usr/bin/python3

# -----------------------------------------
# TestFlow.py
# Script préliminaire pour déclencher une séquence d'observation.
# V 0.01 : 09/12/2023 - F. Cochard - version initiale, qui marche à peu près.
# V 0.02 : 31/12/2023 - F. Cochard - on dispose maintenant de l'initialisation des devices Indi.
# V 0.03 : 07/01/2024 - F. Cochard - j'ajoute le système de Logging (récupéré de ce qu'on avait fait avec Etienne)
#
# L'idée est de pouvoir déclencher une séquence d'observation à partir de l'observatoire, par une API Rest.
# J'ai le choix de la séquence d'observation.
# Pour le moment, je ne passe aucun paramètre, mais je sens que ça pourrait se faire plutôt par un fichier centralisé (ou un json).
# Les différentes séquences possibles (qui correspondent à différents programmes d'observation) sont décrites dans la variable 'sequence'
# Chaque séquence fait appel à des fonctions de "haut niveau" (ici simplifiées en F1, F2, F3 etc)
# J'ai 3 commandes API : run pour lancer, state pour demander dans quel étape est le système, et stop pour interrompre (si la pluie arrive par exemple)
# L'interruption n'est effective qu'à la fin de la fonction Haut Niveau en cours.
# La classe ProcessObs est instanciée à chaque démarrage d'une séquence d'observation. C'est la variable A (on pourrait trouver un meilleur nom :>)
#
#
#
#
#
#
#
# -----------------------------------------

import time
import threading
from fastapi import FastAPI
import uvicorn
import importlib
import yaml
from IPX800_V4.IPX800_V4 import StartAllPSU, StopAllPSU
from utils.LoggingUtils import initLogger
import ObservingSequence.ObservingOperations as SeqOp  # SeqOp means 'Sequence Operation', or a basic operation in an observing sequence.

logger = initLogger("obs")

sequence = {
    "main": {
        "Pointage": SeqOp.F1,
        "Centrage": SeqOp.F1,
        "Guidage": SeqOp.F3,
        "Acquisition": SeqOp.TakeOneImage,
        "Flat": SeqOp.F4,
        "Dark": SeqOp.F5,
    },
    "basic": {"Pointage": SeqOp.F1},
    "BeUVEX": {
        "Pointage": SeqOp.RawPointingTelescope,
        "Centrage": SeqOp.PrecisePointingTelescope,
        "Guidage": SeqOp.ActivateAutoguiding,
        "Acquisition": SeqOp.TakeTargetSpectraSeries,
        "StopGuiding": SeqOp.StopAutoguiding,
        "Calibration": SeqOp.TakeCalibSpectraSeries,
        "Flat": SeqOp.TakeFlatSpectraSeries,
        "Dark": SeqOp.TakeDarkSeries,
        "Bias": SeqOp.TakeBiasSeries,
        "CreateObsFile": SeqOp.CreateObservationFile,
    },
    "seq1": {
        "Pointer": SeqOp.F1,
        "Centrer": SeqOp.TakeOneImage,
        "Acquisition": SeqOp.F3,
    },
    "seq2": {
        "Guider": SeqOp.F1,
        "Acquisition": SeqOp.TakeOneImage,
        "Flat": SeqOp.F4,
        "Dark": SeqOp.F5,
    },
}

# ObsData is the dictionnary that contains all the data required to run and record an observation.
# This ObsData is given as the single parameter to all the operations of an observation.
ObsData = {"Observatory": {}, "Devices": {}, "Observation": {}}
ObsData["Observatory"] = {
    "site": "St-Pancrasse",
    "observer": "F. Cochard",
    "instrument": "UVEX 600",
    # A mettre dans un fichier de config...
}
ObsData["Observation"] = {
    "nb": 3,
    "exptime": 5,
    "x1": 100,
    "y1": 250,
    "x2": 1500,
    "y2": 1400,
    "seq": "BeUVEX",
    "obsfilename": "toto.yaml",
}


class ProcessObs:

    def __init__(self, obs_data):
        self.obs_data = obs_data
        self.seq = sequence[obs_data["Observation"]["seq"]]
        self.err = "OK"
        self.ix = "none"
        self.stop = False
        self.X = threading.Thread(target=self.observing_process_thread)
        self.X.start()

    def observing_process_thread(self):
        for step in self.seq:
            if self.stop == True:
                print("Process interrompu")
                break
            if self.err == "OK":
                self.ix = step
                self.err = self.seq[step](self.obs_data)
            else:
                print("BUG")
                break

    def stop_process(self, message_stop):
        self.stop = True
        print("Interruption du process : ", message_stop)


def ObsProcessRun():
    global A
    if "A" in globals() and A.X.is_alive() == True:
        return "Le process tourne déjà"
    else:
        seq = ObsData["Observation"]["seq"]
        if seq in sequence.keys():
            logger.info(f"We run the process '{seq}'")
            A = ProcessObs(ObsData)
            reply = "Processus démarré : " + seq
            return reply
        else:
            logger.warning(
                f"Process '{seq}' requested, but cannot be ran : does not exist"
            )
            return "Processus inconnu"


def ObsProcessStop(message_stop):
    global A
    if "A" in globals() and A.X.is_alive() == True:
        A.stop_process(message_stop)
        return True
    else:
        print("The process is not running")
        return False


def ObsState():
    global A
    if "A" in globals():
        if A.X.is_alive():
            return A.X.is_alive(), str(A.ix)
        else:
            return False, "Not running"
    else:
        return False, "Not running"


def ReadYamlConfig(Fichier):
    with open(Fichier, "r") as file:
        config_data = yaml.safe_load(file)
    return config_data


def CreatIndiDevices(config_data):
    Devices = {}
    DevicesList = list(config_data)
    for i in DevicesList:
        ModuleName = config_data[i]["module"]
        try:
            moduleDir = config_data[i]["module_dir"]
            device_module = importlib.import_module(moduleDir + "." + ModuleName)
            class_name = config_data[i]["class_name"]
            Devices[i] = getattr(device_module, class_name)(
                config=config_data[i], logger=logger, connect_on_create=False
            )
            message = (
                "Device creation OK: " + ModuleName + " / " + class_name
            )  # + " // " + Devices[i]
            logger.info(message)
        except:
            message = "Exception during device creation: " + ModuleName
            logger.error(message)
    ObsData["Devices"] = Devices
    print("Dev : ", Devices)
    return True


def ConnectDevices():
    for dev in list(ObsData["Devices"]):
        device = ObsData["Devices"][dev]
        print("CONNEXION  :", device)
        device.connect()
        message = "Device Connexion OK: " + str(device)
        logger.info(message)


def DisconnectDevices():
    for dev in list(ObsData["Devices"]):
        device = ObsData["Devices"][dev]
        device.disconnect_device()
        message = "Device disonnexion: " + str(device)
        logger.info(message)


app = FastAPI()


@app.get("/state")
async def get_state():
    return ObsState()


@app.get("/run")
async def get_run():
    print("Ici : ", ObsData["Observation"]["seq"])
    ObsProcessRun()
    return True


@app.get("/stop/{message_stop}")
async def get_stop(message_stop):
    ObsProcessStop(message_stop)
    return True


@app.get("/startupdevices")
async def get_startupdevices():
    configINDIdevices = ReadYamlConfig("IndiDevices/device_config.yaml")
    CreatIndiDevices(configINDIdevices)
    ConnectDevices()
    # Pour mémoire (feb 2024), je peux ajouter ici la lecture du fichier de config de PHD2... à réfléchir
    return True


@app.get("/disconnectdevices")
async def get_disconnectdevices():
    DisconnectDevices()
    return True


@app.get("/takeimage")
async def get_takeimage():
    print("Et là...", ObsData["Devices"])
    camera = ObsData["Devices"]["science_camera"]
    print("data : ", camera)
    print("Jusque ici OK ")
    SeqOp.TakeImage(ObsData, "TOTO.fits")
    return True


@app.get("/startupallpsu")
async def get_startupallpsus():

    StartAllPSU()
    return True


@app.get("/stopallpsu")
async def get_StopAllPSU():
    StopAllPSU()
    return True


if __name__ == "__main__":
    logger.info("Starting of ObservingSequence FastAPI server")
    uvicorn.run("ObsSequence:app", host="0.0.0.0", port=1235, reload=True)
