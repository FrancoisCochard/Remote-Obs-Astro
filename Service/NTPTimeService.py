# Basic stuff
import copy
import json
import logging
import traceback

# Time stuff
from datetime import datetime
from datetime import timedelta 
import ntplib
import pytz

# Astropy stuff
from astropy import units as AU
from astropy.time import Time as ATime

# Local stuff
from Service.BaseService import BaseService

class NTPTimeService(BaseService):
    ''' NTPTime Service: one of the only service class that does not inherit
        from Base, because Base needs a time service. That would generate a
        circular dependency.
        Just in case, we designed a BaseService for this purpose
    '''
    DEFAULT_TIMEZONE_STR = 'Europe/Paris'

    def __init__(self, configFileName=None, obs=None, logger=None):
        BaseService.__init__(self)
        if configFileName is None:
            # Default file is ntp.json
            self.configFileName = './conf_files/ntp.json'
        else:
            self.configFileName = configFileName

        # Now configuring
        self.logger.debug('Configuring NTP Time Service with file {}'.format(
                          self.configFileName))

        # Get ntp server from json
        with open(self.configFileName) as jsonFile:  
            data = json.load(jsonFile)
            self.ntpserver = data['ntpserver']

        self.obs = obs
        
        # Finished configuring
        self.logger.debug('Configured NTP Time Service successfully')

    @property
    def timezone(self):
        if not (self.obs is None):
            return self.obs.get_time_zone()
        else:
            return pytz.timezone(self.DEFAULT_TIMEZONE_STR)

    def getTimeStampFromNTP(self):
        cli = ntplib.NTPClient()
        res = cli.request(self.ntpserver, version=3, timeout=5)
        return res.tx_time

    def getUTCFromNTP(self):
        try:
            res = self.getTimeStampFromNTP()
            utc = datetime.utcfromtimestamp(res)
            self.logger.debug('NTP Time Service got UTC from server {} : {}'
                              .format(self.ntpserver,utc))
        except Exception as e:
            #return UTC from local computer
            utc=datetime.utcnow()
            self.logger.error('NTP Time Service cannot get UTC from server {}'
                ', because of error : {}, got UTC from local clock instead: {}'
                .format(self.ntpserver,e,utc))
        return pytz.utc.localize(utc, is_dst=None)

    def getLocalTimeFromNTP(self):
        return self.convert_to_local_time(self.getUTCFromNTP())

    def getLocalDateFromNTP(self):
        return self.getLocalTimeFromNTP().date()

    def getAstropyTimeFromUTC(self):
        if self.obs is None:
            return ATime(self.getUTCFromNTP())
        else:
            return ATime(self.getUTCFromNTP(),
                         location=self.obs.getAstropyEarthLocation())

    def convert_to_local_time(self, utc_time):
        #If naive time, set to utc by default
        if utc_time.tzinfo is None:
            utc_dt = pytz.utc.localize(utc_time, is_dst=None)
        else:
            utc_dt = copy.deepcopy(utc_time)
        return utc_dt.astimezone()

    def convert_to_utc_time(self, local_time):
        #If naive time, set to local by default
        if local_time.tzinfo is None:
            local_dt = self.timezone.localize(local_time, is_dst=None)
        else:
            local_dt = copy.deepcopy(local_time)
        return local_dt.astimezone(pytz.utc)

    def getNextLocalMidnightInUTC(self, target_date=None):
        if target_date is None:
            target_date = self.getLocalTimeFromNTP().date()
        midnight = datetime(2000,1,1).time()
        next_midnight = (datetime.combine(target_date, midnight) +
                         timedelta(days=1))
        return self.convert_to_utc_time(next_midnight)

    def getNextNoonAfterNextMidnightInUTC(self, target_date=None):
        next_midnight = self.getNextMidnightInUTC(target_date)
        next_noon = next_midnight + timedelta(hours=12)
        return self.convert_to_utc_time(next_noon)

    def get_astropy_gast(self):
        """ returns approximate sidereal time
        """
        utc = self.getAstropyTimeFromUTC()
        if not (self.obs is None):
            return utc.sidereal_time( kind='apparent',
                longitude=self.obs.getAstropyEarthLocation().lon)
        return utc.sidereal_time(kind='apparent')

    def get_gast(self):
        return float(self.get_astropy_gast()/AU.hourangle)

    def get_jd(self):
        return self.getAstropyTimeFromUTC().jd

    def flat_time(self):
        """
            Given an astropy Time, flatten to have no extra chars besides
            integers
        """
        t = self.getAstropyTimeFromUTC()
        return t.isot.replace('-', '').replace(':', '').split('.')[0]

