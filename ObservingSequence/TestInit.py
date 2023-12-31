# Script de test pour explorer une initialisation de l'instrumentation...

import yaml
from IndiDevices.Camera.IndiASICamera import IndiASICamera
import time

Fichier = "IndiDevices/device_config.yaml"
with open(Fichier, 'r') as file:
    config_data = yaml.safe_load(file)

# print(donnees.items())
print(list(config_data))

# print(donnees['science_camera'])

data = config_data['science_camera']
print(data)
# t = (data['module'])()
t = IndiASICamera(config=data)
print("Type initial cam : ", type(t))
# print("-> Connexion : ", t.is_connected)
t.connect()
print("Connexion OK")
time.sleep(1)
print("-> Connexion dev: ", t.is_connected)
time.sleep(1)
print("-> Connexion cl: ", t.is_client_connected)
time.sleep(1)
print("-> Connexion device : ", t.is_connected)
time.sleep(1)

print("Maintenant je déconnecte device")
time.sleep(1)
t.disconnect_device()
time.sleep(1)
print("Deconnexion device OK")
time.sleep(1)
print("-> Connexion device : ", t.is_connected)
time.sleep(1)

print("-> Connexion client : ", t.is_client_connected)
time.sleep(1)
print("Maintenant je déconnecte le client")
time.sleep(1)
t.disconnect()
time.sleep(1)
print("Deconnexion OK")
time.sleep(1)
print("-> Connexion : ", t.is_client_connected)