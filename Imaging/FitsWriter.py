#Basic stuff
import datetime
import io
import logging
import threading
import traceback

# Astropy for handling FITS
from astropy.io import fits

# Local stuff

class FitsWriter():
    """
      Check FITS manipulation with astropy:
      http://docs.astropy.org/en/stable/io/fits/
    """

    def __init__(self, logger=None, observatory=None, servWeather=None,
                 servTime=None, servAstrometry=None, filterWheel=None,
                 telescope=None, camera=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug('Configuring FitsWriter')

        self.imgIdx = 0
        self.observatory = observatory
        self.servWeather = servWeather
        self.servTime = servTime
        self.servAstrometry = servAstrometry
        self.filterWheel = filterWheel
        self.telescope = telescope
        self.camera = camera
        self.ephem = None #TODO TN to be improved

        self.threadLock = threading.Lock()

        self.logger.debug('FitsWriter configured successfully')

    def writeWithTag(self, fits, targetName='frame'):
        '''
          First step: tag with every possible information
          Seconnd step: Write fits to disk
        '''
        try:
            try:
                hdr = fits.header
            except:
                hdr = fits[0].header
            
            if self.servTime is not None:
                hdr['UTCTIME'] = (str(self.servTime.getUTCFromNTP()), 'NC')
            if self.filterWheel is not None:
                filterName = self.filterWheel.currentFilter()[1]
                hdr['FILTER'] = (filterName, 'NC')
            if self.camera is not None:
                hdr['EXPOSURETIMESEC'] = (str(self.camera.getExposureTimeSec()),
                                          'NC')
                hdr['GAIN'] = (str(self.camera.getGain()), 'NC')
            if self.observatory is not None:
                hdr['OBSERVER'] = (self.observatory.getOwnerName(), 'NC')
                hdr['GPSCOORD'] = (str(self.observatory.getGpsCoordinates()),
                                   'NC')
                hdr['ALTITUDEMETER'] = (str(self.observatory.getAltitudeMeter()
                                        ), 'NC')
            if self.servWeather is not None:
                hdr['TEMPERATUREC'] = (str(self.servWeather.getTemp_c()), 'NC')
                hdr['RELATIVEHUMIDITY'] = (str(self.servWeather.
                                               getRelative_humidity()), 'NC')
                hdr['WINDKPH'] = (str(self.servWeather.getWind_kph()), 'NC')
                hdr['WINDGUSTKPH'] = (str(self.servWeather.getWind_gust_kph()),
                                      'NC')
                hdr['PRESSUREMB'] = (str(self.servWeather.getPressure_mb()),
                                     'NC')
                hdr['DEWPOINTC'] = (str(self.servWeather.getDewpoint_c()),
                                    'NC')
                hdr['VISIBILITYKM'] = (str(self.servWeather.getVisibility_km()),
                                       'NC')
                hdr['WEATHER'] = (self.servWeather.getWeatherQuality(), 'NC')
            if self.ephem is not None:
                hdr['SUNRISE'] = (str(self.ephem.getSunRiseTime()), 'NC')
                hdr['SUNSET'] = (str(self.ephem.getSunSetTime()), 'NC')
                hdr['SUNHASROSE'] = (str(self.ephem.hasSunRose()), 'NC')
                hdr['MOONILLUMINATEDPERC'] = (str(self.ephem.
                                              getPercentIlluminated()), 'NC')
                hdr['MOONAGEDAY'] = (str(self.ephem.getAgeOfMoon()), 'NC')
                hdr['MOONHASROSE'] = (str(self.ephem.hasMoonRose()), 'NC')
            if self.servAstrometry is not None:
                t=io.BytesIO()
                fits.writeto(t)
                #TODO TN try to input some more informations for solving
                self.servAstrometry.solveImage(t.getvalue())
                hdr['PARITY'] = (str(self.servAstrometry.getCalib()['parity']),
                                 'NC')
                hdr['ORIENTATION'] = (str(self.servAstrometry.getCalib()[
                                          'orientation']), 'NC')
                hdr['PIXSCALE'] = (str(self.servAstrometry.getCalib()[
                                       'pixscale']), 'NC')
                hdr['RADIUS'] = (str(self.servAstrometry.getCalib()['radius']),
                                 'NC')
                hdr['RA'] = (str(self.servAstrometry.getCalib()['ra']), 'NC')
                hdr['DEC'] = (str(self.servAstrometry.getCalib()['dec']), 'NC')
            if self.telescope is not None:
                hdr['TELESCOPE'] = (str(self.telescope.getName()), 'NC')
                hdr['FOCALLENGHT'] = (str(self.telescope.getFocale()), 'NC')
                hdr['DIAMETER'] = (str(self.telescope.getDiameter()), 'NC')
                hdr['TELESCOPERA'] = (str(self.telescope.getCurrentSkyCoord()[
                                          'RA']), 'NC')
                hdr['TELESCOPEDEC'] = (str(self.telescope.getCurrentSkyCoord()[
                                           'DEC']), 'NC')
            if targetName is not None:
                hdr['TARGETNAME'] = (targetName, 'NC')

            # Last comment then write everything to disk
            hdr['COMMENT'] = 'No generic comment, life is beautiful'
        except Exception as e:
            self.logger.error('FitsWriter error while tagging fit with index '
                              ' {} : {}'.format(self.imgIdx,e))

        filename='{}-{}.fits'.format(targetName,self.imgIdx)
        try:
            with open(filename, "wb") as f:
                fits.writeto(f, overwrite=True)
                with self.threadLock:
                    self.imgIdx += 1
        except Exception as e:
            self.logger.error('FitsWriter error while writing file {} : {}'
                              ''.format(filename,e))

