# Basic stuff
import logging
import logging.config


# Local stuff
from Observatory.VirtualObservatory import VirtualObservatory
from Observatory.ShedObservatory import ShedObservatory
from Service.VirtualService import VirtualService
from Service.WUGMoonService import WUGMoonService


if __name__ == '__main__':

  # load the logging configuration
  logging.config.fileConfig('logging.ini')
  logger = logging.getLogger('mainLogger')

  # Instanciate object of interest
  #obs = VirtualObservatory(logger=logger)
  obs = ShedObservatory(logger=logger)
  serv = WUGMoonService(logger=logger)
  
