#!/usr/bin/python3

# -----------------------------------------
# Sequence.py
# Script préliminaire (de moins en moins, en fait) pour déclencher une séquence d'observation.
# V 0.01 : 09/12/2023 - F. Cochard - version initiale, qui marche à peu près.
# V 0.02 : 31/12/2023 - F. Cochard - on dispose maintenant de l'initialisation des devices Indi.
# V 0.03 : 07/01/2024 - F. Cochard - j'ajoute le système de Logging (récupéré de ce qu'on avait fait avec Etienne)
# V 0.05 : 06/04/2025 - F. Cochard - je transforme l'organisation des fichiers (low_level, high_level, API, etc)
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
# Le 06/04/2025, je transforme l'orgaisation générale, pour aller vers un truc plus ambitieux
# L'idée est de mettre dans ce fichier toute la mécanique qui gère la séquence d'opérations.
#
#
#
#
# -----------------------------------------

import threading
import importlib
import yaml
from Module3_Sequencer.IPX800_V4.IPX800_V4 import StartAllPSU, StopAllPSU
from Module3_Sequencer.utils.LoggingUtils import initLogger
import Module3_Sequencer.ObservingSequence.High_level_operations as hilev  # hilev means 'High Level Operation', or a rich operation in an observing sequence.

logger = initLogger("obs")

sequence = {
    "main": {
        "Pointage": hilev.F1,
        "Centrage": hilev.F1,
        "Guidage": hilev.F3,
        "Acquisition": hilev.TakeScienceImage,
        "Flat": hilev.F4,
        "Dark": hilev.F5,
    },
    "basic": {"Pointage": hilev.F1},
    "BeUVEX": {
        "Pointage": hilev.lowlev.PointingTelescopeToCoord,
        "Centrage": hilev.PointingTelescope,
        "Guidage": hilev.ActivateAutoguiding,
        "Acquisition": hilev.lowlev.TakeTargetSpectraSeries,
        "StopGuiding": hilev.StopAutoguiding,
        "Calibration": hilev.lowlev.TakeCalibSpectraSeries,
        "Flat": hilev.lowlev.TakeFlatSpectraSeries,
        "Dark": hilev.lowlev.TakeDarkSeries,
        "Bias": hilev.lowlev.   TakeBiasSeries,
        "CreateObsFile": hilev.CreateObservationFile,
    },
    "seq1": {
        "Pointer": hilev.F1,
        "Centrer": hilev.TakeScienceImage,
        "Acquisition": hilev.F3,
    },
    "seq2": {
        "Guider": hilev.F1,
        "Acquisition": hilev.TakeScienceImage,
        "Flat": hilev.F4,
        "Dark": hilev.F5,
    },
}

# ObsData is the dictionnary that contains all the data required to run and record an observation.
# This ObsData is given as the single parameter to all the operations of an observation.
# ObsData = {"Observatory": {}, "Devices": {}, "Observation": {}}
ObsData = {"Devices": {}}
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
    """To start the Observing process"""
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
        device.connect()
        message = "Device Connexion OK: " + str(device)
        logger.info(message)


def DisconnectDevices():
    for dev in list(ObsData["Devices"]):
        device = ObsData["Devices"][dev]
        device.disconnect_device()
        message = "Device disonnexion: " + str(device)
        logger.info(message)


def PointingTEST(TargetCoord):
    print(f"Ici, OK {ObsData}")
    hilev.PointingTelescopeToCoord(ObsData, TargetCoord)

def test():
    print("Hello...")
