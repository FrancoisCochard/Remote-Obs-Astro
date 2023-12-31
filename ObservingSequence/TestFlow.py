# -----------------------------------------
# TestFlow.py
# Script préliminaire pour déclencher une séquence d'observation.
# V 0.01 : 09/12/2023 - F. Cochard - version initiale, qui marche à peu près.
# 
# L'idée est de pouvoir déclencher une séquence d'observation à partir de l'observatoire, par une API Rest.
# J'ai le choix de la séquence d'observation.
# Pour le moment, je ne passe aucun paramètre, mais je sens que ça pourrait se faire plutôt par un fichier centralisé (ou un json).
# Les différentes séquences possibles (qui correspondent à différents programmes d'observation) sont décrites dans la variable 'sequence'
# Chaque séquence fait appel à des fonctions de "haut niveau" (ici simplifiées en F1, F2, F3 etc)
# J'ai 3 commandes API : run pour lancer, state pour demander dans quel étape est le système, et stop pour interrompre (si la pluie arrive par exemple)
# L'interruption n'est effective qu'à la fin de la fonction Haut Niveau en cours.
# La classe ProcessObs est instanciée à chaque démarrage d'une séquence d'onservation. C'est la variable A (on pourrait trouver un meilleur nom :>)
# 
# -----------------------------------------

import time
import threading
from fastapi import FastAPI
import uvicorn
from IndiDevices.Camera.IndiASICamera import IndiASICamera
import yaml

def F1():
    print("F1 - début")
    time.sleep(3)
    print("F1 - fin")
    return "OK"

def TakeOneImage():
    print("Acquisition - début")
    # time.sleep(3)
    camera = devices_list['ScienceCam']
    TakeImage(camera)
    print("Acquisition - fin")
    return "OK"

def F3():
    print("F3 - début")
    time.sleep(3)
    print("F3 - fin")
    return "OK"

def F4():
    print("F4 - début")
    time.sleep(3)
    print("F4 - fin")
    return "OK"

def F5():
    print("F5 - début")
    time.sleep(3)
    print("F5 - fin")
    return "OK"

sequence = {
'main':{"Pointage":F1, "Centrage":F1, "Guidage":F3, "Acquisition":TakeOneImage, "Flat":F4, "Dark":F5},
'seq1':{"Pointer":F1, "Centrer":TakeOneImage, "Acquisition":F3},
'seq2':{"Guider":F1, "Acquisition":TakeOneImage, "Flat":F4, "Dark":F5}
}

devices_list = {}

class ProcessObs:
    
    def __init__(self, seq):
        self.seq = seq
        self.err = "OK"
        self.ix = 'none'
        self.stop = False
        self.X = threading.Thread(target = self.observing_process_thread)
        self.X.start()
    
    def observing_process_thread(self):
        for step in self.seq:
            if self.stop == True:
                print("Process interrompu")
                break
            if self.err == "OK":
                self.ix = step
                self.err = self.seq[step]()
            else :
                print("BUG")
                break
    
    def stop_process(self, message_stop):
        self.stop = True
        print("Interruption du process : ", message_stop)

def ObsProcessRun(process):
    global A
    if 'A' in globals() and A.X.is_alive() == True:
        return "Le process tourne déjà"
    else:
        if process in sequence.keys():
            A = ProcessObs(sequence[process])
            reply = "Processus démarré : " + process
            return reply
        else:
            return "Processus inconnu"

def ObsProcessStop(message_stop):
    global A
    if 'A' in globals() and A.X.is_alive() == True:
        A.stop_process(message_stop)
        return True
    else:
        print("The process is not running")
        return False
        
def ObsState():
    global A
    if 'A' in globals():
        if A.X.is_alive():
            return A.X.is_alive(), str(A.ix)
        else:
            return False, "Not running"
    else:
        return False, "Not running"

def ReadDevicesConfig(Fichier):
    with open(Fichier, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data

def CreatIndiDevices(config_data):
    
    # Create ScienceCamera
    config = config_data['science_camera']
    science_cam = IndiASICamera(config=config)
    devices_list['ScienceCam'] = science_cam
    print("Science Camera: ", science_cam)

    print(devices_list)
    return True

def StartUpDevices():
    for dev in list(devices_list):
        device = devices_list[dev]
        device.connect()
        print("Device ", device.name, "connecté")

def DisconnectDevices():
    for dev in list(devices_list):
        device = devices_list[dev]
        device.disconnect_device()
        print("Device ", device.name, "déconnecté")

def TakeImage(science_cam):
    if science_cam.is_connected:
        # science_cam = devices_list[Science]
        science_cam.prepare_shoot()
        science_cam.setExpTimeSec(2)
        print("Je vais démarrer la pose")
        science_cam.shoot_async()
        print("J'ai lancé le shoot_async")
        science_cam.synchronize_with_image_reception()
        print("Terminé le synchronize")
        fitsIm = science_cam.get_received_image()
        print("Image reçue !")
        ImName = "TESTAEFFACER.fits"
        fitsIm.writeto(ImName, overwrite=True)
    else:
        print("Device pas connecté")

app = FastAPI()

@app.get("/state")
async def get_state():
    return ObsState()

@app.get("/run/{process}")
async def get_run(process):
    return ObsProcessRun(process)

@app.get("/stop/{message_stop}")
async def get_stop(message_stop):
    ObsProcessStop(message_stop)
    return True

@app.get("/startupdevices")
async def get_startupdevices():
    config = ReadDevicesConfig("IndiDevices/device_config.yaml")
    CreatIndiDevices(config)
    StartUpDevices()
    return True

@app.get("/disconnectdevices")
async def get_disconnectdevices():
    # config = ReadDevicesConfig("IndiDevices/device_config.yaml")
    DisconnectDevices()
    return True

@app.get("/takeimage")
async def get_takeimage():
    print("Et là...", devices_list)
    camera = devices_list['ScienceCam']
    print("data : ", camera)
    print("type : ", type(camera))
    TakeImage(camera)
    return True

if __name__ == "__main__":
    print("On démarre")
    uvicorn.run("TestFlow:app", host="0.0.0.0", port=1235, reload=True)
