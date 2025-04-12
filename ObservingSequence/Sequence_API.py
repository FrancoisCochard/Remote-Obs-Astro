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

from fastapi import FastAPI

import uvicorn
from utils.LoggingUtils import initLogger
import Sequence as sq

logger = initLogger("obs")

app = FastAPI()


@app.get("/state")
async def get_state():
    return sq.ObsState()


@app.get("/run")
async def get_run():
    print("Ici : ", sq.ObsData["Observation"]["seq"])
    sq.ObsProcessRun()
    return True


@app.get("/TEST-pointage")
async def get_pointingTest():
    # print("Ici : ", ObsData["Observation"]["seq"])
    sq.lowlev.PointingTelescope()
    return True


@app.get("/stop/{message_stop}")
async def get_stop(message_stop):
    sq.ObsProcessStop(message_stop)
    return True


@app.get("/startupdevices")
async def get_startupdevices():
    configINDIdevices = sq.ReadYamlConfig("IndiDevices/device_config.yaml")
    sq.CreatIndiDevices(configINDIdevices)
    sq.ConnectDevices()
    # Pour mémoire (feb 2024), je peux ajouter ici la lecture du fichier de config de PHD2... à réfléchir
    return True


@app.get("/disconnectdevices")
async def get_disconnectdevices():
    sq.DisconnectDevices()
    return True


@app.get("/takeScienceImage", tags=["2. High level operations"])
async def get_takescienceimage(Exptime=1.0, Nb=1, Name=''):
    # print("Et là...", sq.ObsData["Devices"], Exptime, Nb)
    camera = sq.ObsData["Devices"]["science_camera"]
    print("data : ", camera)
    # print("Jusque ici OK ")
    sq.hilev.TakeScienceImage(camera, Nb, Exptime, Name)
    # sq.hilev.test()
    return True

@app.get("/takeGuideImage", tags=["2. High level operations"])
async def get_takeguideimage():
    print("pour info : ", sq.ObsData["Devices"])
    camera = sq.ObsData["Devices"]["guiding_camera"]
    print("data : ", camera)
    print("Jusque ici OK (guidage) ")
    sq.hilev.TakeGuideImage(camera, 1, 1.0)
    # sq.hilev.test()
    return True


@app.get("/startupallpsu")
async def get_startupallpsus():

    sq.StartAllPSU()
    return True


@app.get("/stopallpsu")
async def get_StopAllPSU():
    sq.StopAllPSU()
    return True


@app.get("/startInstrument", tags=["1. Main operations"])
async def get_startInstrument():
    sq.StartAllPSU()
    configINDIdevices = sq.ReadYamlConfig("IndiDevices/device_config.yaml")
    sq.CreatIndiDevices(configINDIdevices)
    sq.ConnectDevices()
    return True


@app.get("/stopInstrument", tags=["1. Main operations"])
async def get_stopInstrument():
    sq.DisconnectDevices()
    sq.StopAllPSU()
    return True


@app.get("/startObserving")
async def get_startObserving():

    observingAgreement = True
    return True


@app.get("/stopObserving")
async def get_stopObserving():

    observingAgreement = False
    return True


@app.get("/PointageTelescope")
async def get_pointing():

    TargetCoord = sq.SkyCoord("03h13m43s +15d34m31s", frame="icrs")
    sq.PointingTEST(TargetCoord)
    return True


if __name__ == "__main__":
    logger.info("Starting of Observing Sequence FastAPI server")
    uvicorn.run("Sequence_API:app", host="0.0.0.0", port=1235, reload=True)
