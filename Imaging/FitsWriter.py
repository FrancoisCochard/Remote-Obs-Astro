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
      servSun=None, servMoon=None, servTime=None, servAstrometry=None,
      filtWheel=None, telescope=None, camera=None, target=None):
    self.logger = logger or logging.getLogger(__name__)
    self.logger.debug('Configuring FitsWriter')

    self.imgIdx = 0
    self.observatory = observatory
    self.servWeather = servWeather
    self.servSun = servSun
    self.servMoon = servMoon
    self.servTime = servTime
    self.servAstrometry = servAstrometry
    self.filtWheel = filtWheel
    self.telescope = telescope
    self.camera = camera
    self.target = target

    self.threadLock = threading.Lock()

    self.logger.debug('FitsWriter configured successfully')

  def writeWithTag(self, fits):
    '''
      First step: tag with every possible information
      Secnd step: Write fits to disk
    '''
    try:
      hdr = fits.header
      
      if self.observatory is not None:
        hdr['OBSERVER'] = (self.observatory.getOwnerName(), 'NC')
        hdr['GPSCOORD'] = (str(self.observatory.getGpsCoordinates()), 'NC')
        hdr['ALTITUDEMETER'] = (str(self.observatory.getAltitudeMeter()), 'NC')
      if self.servWeather is not None:
        hdr['TEMPERATUREC'] = (str(self.servWeather.getTemp_c()), 'NC')
        hdr['RELATIVEHUMIDITY'] = (str(self.servWeather.getRelative_humidity())\
          , 'NC')
        hdr['WINDKPH'] = (str(self.servWeather.getWind_kph()), 'NC')
        hdr['WINDGUSTKPH'] = (str(self.servWeather.getWind_gust_kph()), 'NC')
        hdr['PRESSUREMB'] = (str(self.servWeather.getPressure_mb()), 'NC')
        hdr['DEWPOINTC'] = (str(self.servWeather.getDewpoint_c()), 'NC')
        hdr['VISIBILITYKM'] = (str(self.servWeather.getVisibility_km()), 'NC')
        hdr['WEATHER'] = (self.servWeather.getWeatherQuality(), 'NC')
      if self.servSun is not None:
        hdr['SUNRISE'] = (str(self.servSun.getSunRiseTime()), 'NC')
        hdr['SUNSET'] = (str(self.servSun.getSunSetTime()), 'NC')
        hdr['SUNHASROSE'] = (str(self.servSun.hasSunRose()), 'NC')
      if self.servMoon is not None:
        hdr['MOONILLUMINATEDPERC'] = (str(self.servMoon.getPercentIlluminated()\
          ), 'NC')
        hdr['MOONAGEDAY'] = (str(self.servMoon.getAgeOfMoon()), 'NC')
        hdr['MOONHASROSE'] = (str(self.servMoon.hasMoonRose()), 'NC')
      if self.servTime is not None:
        hdr['UTCTIME'] = (str(self.servTime.getUTCFromNTP()), 'NC')
      if self.servAstrometry is not None:
        t=io.BytesIO()
        fits.writeto(t)
        self.servAstrometry.solveImage(t.getvalue())
        hdr['PARITY'] = (str(self.servAstrometry.getCalib()['parity']), 'NC')
        hdr['ORIENTATION'] = (str(self.servAstrometry.getCalib()['orientation'\
          ]), 'NC')
        hdr['PIXSCALE'] = (str(self.servAstrometry.getCalib()['pixscale']),\
          'NC')
        hdr['RADIUS'] = (str(self.servAstrometry.getCalib()['radius']), 'NC')
        hdr['RA'] = (str(self.servAstrometry.getCalib()['ra']), 'NC')
        hdr['DEC'] = (str(self.servAstrometry.getCalib()['dec']), 'NC')
      if self.filtWheel is not None:
        hdr['FILTER'] = (self.filtWheel.getCurrentFilterName(), 'NC')
      if self.telescope is not None:
        hdr['TELESCOPE'] = (str(self.telescope.getName()), 'NC')
        hdr['FOCALLENGHT'] = (str(self.telescope.getFocale()), 'NC')
        hdr['DIAMETER'] = (str(self.telescope.getDiameter()), 'NC')
        hdr['TELESCOPERA'] = (str(self.telescope.getCurrentSkyCoord()['RA']),\
          'NC')
        hdr['TELESCOPEDEC'] = (str(self.telescope.getCurrentSkyCoord()['DEC'])\
          , 'NC')
      if self.camera is not None:
        hdr['EXPOSURETIMESEC'] = (str(self.camera.getExposureTimeSec()), 'NC')
        hdr['GAIN'] = (str(self.camera.getGain()), 'NC')
      if self.target is not None:
        hdr['TARGETNAME'] = (self.target.getTargetName(), 'NC')

      # Last comment then write everything to disk
      hdr['COMMENT'] = 'No generic comment, life is beautiful'
    except Exception as e:
      self.logger.error('FitsWriter error while tagging fit with index '+\
        str(self.imgIdx)+' : '+str(e)+traceback.format_exc())

    filename="frame"+str(self.imgIdx)+".fits"
    try:
      with open(filename, "wb") as f:
        fits.writeto(f, overwrite=True)
        with self.threadLock:
          self.imgIdx += 1
    except Exception as e:
      self.logger.error('FitsWriter error while writing file '+filename+\
        ' : '+str(e))

