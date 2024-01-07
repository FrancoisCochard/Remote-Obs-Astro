#!/usr/bin/python3

# ----------------------------------------------
# Script de Test du système de log. F. Cochard, 07/01/2024.
# On s'appuie sur le script LoggingUtils.py qui s'occupe de tout.
# Le fichier de config de tout le système de logging est dans utils/logger.cfg
# Testé et validé le 07/01/2024
# ----------------------------------------------
 
from utils.LoggingUtils import initLogger

Logger = initLogger('obs')

Logger.debug("Test Debug")
Logger.warning("Test Warning")
Logger.info("Test Info")
Logger.critical("Test Critical")
