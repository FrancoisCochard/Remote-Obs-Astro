# Basic stuff
import json
import logging
import traceback

# Time stuff
from datetime import datetime
import ntplib

# Local stuff
from Service.BaseService import BaseService

class NTPTimeService(BaseService):
    ''' NTPTime Service:
    '''
    
    def __init__(self, configFileName=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        if configFileName is None:
            # Default file is ntp.json
            self.configFileName = 'ntp.json'
        else:
            self.configFileName = configFileName

        # Now configuring
        self.logger.debug('Configuring NTP Time Service with file {}'.format(
                          self.configFileName))

        # Get ntp server from json
        with open(self.configFileName) as jsonFile:  
            data = json.load(jsonFile)
            self.ntpserver = data['ntpserver']
        
        # Finished configuring
        self.logger.debug('Configured NTP Time Service successfully')

    def getUTCFromNTP(self):
        try:
            cli = ntplib.NTPClient()
            res = cli.request(self.ntpserver, version=3, timeout=5)
            utc=datetime.utcfromtimestamp(res.tx_time)
            self.logger.debug('NTP Time Service got UTC from server {} : {}'
                              .format(self.ntpserver,utc))
            return utc
        except Exception as e:
            #return UTC from local computer
            utc=datetime.utcnow()
            self.logger.error('NTP Time Service cannot get UTC from server {}'
                ', because of error : {}, got UTC from local clock instead: {}'
                .format(self.ntpserver,e,utc))
            return utc


