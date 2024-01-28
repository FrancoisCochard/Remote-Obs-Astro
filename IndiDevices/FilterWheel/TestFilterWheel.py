'''
This script is made to test the Indi Filter wheel device
F. Cochard - Jan 2024
'''
import importlib
import yaml
import time
from utils.LoggingUtils import initLogger

logger = initLogger('obs')

Fichier = "IndiDevices/device_config.yaml"
with open(Fichier, 'r') as file:
    config_data = yaml.safe_load(file)
print(list(config_data))
data = config_data['filter_wheel']
print(data, " - ", type(data))

nom_dir = "IndiDevices.FilterWheel"
nom_module = "IndiFilterWheel"
chemin_module = nom_dir + '.' + nom_module
module = importlib.import_module(chemin_module)
nom_classe = "IndiFilterWheel"
ma_classe = getattr(module, nom_classe)
print('Je passe là')
instance = ma_classe(config=data, logger=logger)
print('Et encore...')
instance.connect()
while instance.is_connected == False:
    time.sleep(1)
    print("-> Connexion dev: ", instance.is_connected)
print("At the end, connexion : ", instance.is_connected)

print("Initialization")
instance.initFilterWheelConfiguration()
print("Initialization OK")

print("List of filters :")
print(instance.filters())
print("Filters OK")

print("Filter name of filter #3:", instance.filterName(3))

print("Current filter :", instance.currentFilter())
print("Set filter 530nm")
instance.set_filter('530nm')
print("Current filter :", instance.currentFilter())
print("Set filter number 4")
instance.set_filter_number(4)
print("Current filter :", instance.currentFilter())

print("__str__ : ", instance.__str__())
print("__repr__ : ", instance.__repr__())

