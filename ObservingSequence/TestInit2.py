import importlib
import yaml
import time

Fichier = "IndiDevices/device_config.yaml"
with open(Fichier, 'r') as file:
    config_data = yaml.safe_load(file)
print(list(config_data))
# data = config_data['science_camera']
data = config_data['mount']
print(data, " - ", type(data))

nom_dir = "IndiDevices.Mount"
nom_module = "IndiMount"
chemin_module = nom_dir + '.' + nom_module
module = importlib.import_module(chemin_module)
nom_classe = "IndiMount"
ma_classe = getattr(module, nom_classe)
instance = ma_classe(config=data)
instance.connect()
while instance.is_connected == False:
    time.sleep(1)
    print("-> Connexion dev: ", instance.is_connected)
print("Finalement, connexion dev: ", instance.is_connected)