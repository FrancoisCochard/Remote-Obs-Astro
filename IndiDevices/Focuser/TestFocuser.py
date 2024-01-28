'''
This script is made to test the Indi Filter wheel device
F. Cochard - Jan 2024
'''
import importlib
import yaml
import time

Fichier = "IndiDevices/device_config.yaml"
with open(Fichier, 'r') as file:
    config_data = yaml.safe_load(file)
print(list(config_data))
# data = config_data['science_camera']
data = config_data['focuser']
print(data, " - ", type(data))

nom_dir = "IndiDevices.Focuser"
nom_module = "IndiFocuser"
chemin_module = nom_dir + '.' + nom_module
module = importlib.import_module(chemin_module)
nom_classe = "IndiFocuser"
ma_classe = getattr(module, nom_classe)
print('Toujours là')
instance = ma_classe(config=data)
print('Et encore...')
instance.initialize()
while instance.is_connected == False:
    time.sleep(1)
    print("-> Connexion dev: ", instance.is_connected)
print("Finalement, connexion dev: ", instance.is_connected)

print("Position : ", instance.get_position())