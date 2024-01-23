# Script de test pour explorer une initialisation de l'instrumentation...

import yaml
from IndiDevices.Camera.IndiASICamera import IndiASICamera
# from IndiDevices.Mount.Indi10micronMount import Indi10micronMount
from IndiDevices.Mount.IndiMount import IndiMount
import time

Fichier = "IndiDevices/device_config.yaml"
with open(Fichier, 'r') as file:
    config_data = yaml.safe_load(file)

# print(donnees.items())
print(list(config_data))

# print(donnees['science_camera'])

data = config_data['science_camera']
# data = config_data['mount']
print(data)
# t = (data['module'])()
t = IndiASICamera(config=data)
# t = IndiMount(config=data)
print("Type initial cam : ", type(t))
# print("-> Connexion : ", t.is_connected)
t.connect()
print("Connexion OK")
time.sleep(1)
while t.is_connected == False:
    time.sleep(1)
    print("-> Connexion dev: ", t.is_connected)
print("Finalement, connexion dev: ", t.is_connected)


# print("-> Connexion cl: ", t.is_client_connected)
# time.sleep(1)
# print("-> Connexion device : ", t.is_connected)
# time.sleep(1)

# print("Maintenant je déconnecte device")
# time.sleep(1)
time.sleep(5)
t.disconnect_device()
time.sleep(1)
print("Deconnexion device OK")
# time.sleep(1)
# print("-> Connexion device : ", t.is_connected)
# time.sleep(1)

# print("-> Connexion client : ", t.is_client_connected)
# time.sleep(1)
# print("Maintenant je déconnecte le client")
# time.sleep(1)
# t.disconnect()
# time.sleep(1)
# print("Deconnexion OK")
# time.sleep(1)
# print("-> Connexion : ", t.is_client_connected)