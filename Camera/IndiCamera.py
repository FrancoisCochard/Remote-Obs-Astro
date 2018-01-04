#Basic stuff
import io
import json
import logging
import threading

#Indi stuff
import PyIndi
from helper.IndiDevice import IndiDevice

class CameraSettingsRunner:
  def __init__(self, camera, roi=None, binning=None,\
      compressionFormat=None, frameType=None, properties=None, numbers=None,
      switches=None):
    self.camera = camera
    self.roi = roi
    self.binning = binning
    self.compressionFormat = compressionFormat
    self.frameType = frameType
    self.properties = properties
    self.numbers = numbers
    self.switches = switches

  def run(self):
    if self.roi:
      self.camera.setRoi(self.roi)
    if self.binning:
      self.camera.setBinning(self.binning)
    if self.compressionFormat:
      self.camera.setCompressionFormat(self.compressionFormat)
    if self.frameType:
      self.camera.setFrameType(self.frameType)
    if self.properties:
      self.camera.setProperties(self.properties)
    if self.numbers:
      for propName, valueVector in self.numbers.items():
        self.camera.setNumber(propName, valueVector)
    if self.switches:
      for propName, valueVector in self.switches.items():
        self.camera.setSwitch(propName, valuesVector['on']\
          if 'on' in valueVector else [], valueVector['off']\
          if 'off' in valueVector else [])

  def __str__(self):
    values = [['roi', self.roi],\
      ['bin', self.binning],\
      ['compressionFormat', self.compressionFormat],\
      ['frameType', self.frameType],\
      ['properties', self.properties],\
      ['numbers', self.numbers],\
      ['switches', self.switches]]
    values = [': '.join([x[0], str(x[1])]) for x in values if x[1]]
    return 'Change camera settings: {0}'.format(', '.join(values))

  def __repr__(self):
      return self.__str__()

class IndiCamera(IndiDevice):
  ''' Indi Camera '''

  UploadModeDict = {'local': 'UPLOAD_LOCAL',
    'client': 'UPLOAD_CLIENT',\
    'both': 'UPLOAD_BOTH'}

  def __init__(self, indiClient, logger=None, configFileName=None,\
      connectOnCreate=True):
    logger = logger or logging.getLogger(__name__)
    
    if configFileName is None:
      self.cameraName = 'CCD Simulator'
    else:
      self.configFileName = configFileName
      # Now configuring class
      logger.debug('Configuring Indi Camera with file %s',\
        self.configFileName)
      # Get key from json
      with open(self.configFileName) as jsonFile:
        data = json.load(jsonFile)
        self.cameraName = data['cameraName']

    logger.debug('Indi camera, camera name is: '+\
      self.cameraName)
  
    # device related intialization
    IndiDevice.__init__(self, logger=logger, deviceName=self.cameraName,\
      indiClient=indiClient)
    if connectOnCreate:
      self.connect()

    # Finished configuring
    self.logger.debug('Configured Indi Camera successfully')

  def onEmergency(self):
    self.logger.debug('Indi Camera: on emergency routine started...')
    pass
    self.logger.debug('Indi Camera: on emergency routine finished')

  '''
    Indi CCD related stuff
  '''
  def prepareShoot(self):
    '''
      We should inform the indi server that we want to receive the
      "CCD1" blob from this device
    '''
    self.indiClient.setBLOBMode(PyIndi.B_ALSO, self.deviceName, 'CCD1')

  def shoot(self, expTimeSec):
    self.logger.info('Indi Camera: launching acquisition with '+\
      str(expTimeSec)+' sec exposure time')
    self.setNumber('CCD_EXPOSURE', {'CCD_EXPOSURE_VALUE': expTimeSec},\
      timeout=5+expTimeSec*1.5)

  def setUploadPath(self, path, prefix = 'IMAGE_XXX'):
    self.setText('UPLOAD_SETTINGS', {'UPLOAD_DIR': path,\
      'UPLOAD_PREFIX': prefix})

  def getBinning(self):
    return self.getPropertyValueVector('CCD_BINNING', 'number')

  def setBinning(self, hbin, vbin = None):
    if vbin == None:
      vbin = hbin
    self.setNumber('CCD_BINNING', {'HOR_BIN': hbin, 'VER_BIN': vbin })

  def getRoi(self):
    return self.getPropertyValueVector('CCD_FRAME', 'number')

  def setRoi(self, roi):
    self.setNumber('CCD_FRAME', roi)

  def getCompressionFormat(self):
    return self.switchValues('CCD_COMPRESSION')

  def setCompressionFormat(self, ccdCompression):
    self.setSwitch('CCD_COMPRESSION', [ccdCompression])

  def getFrameType(self):
    return self.switchValues('CCD_FRAME_TYPE')

  def setFrameType(self, frame_type):
    self.setSwitch('CCD_FRAME_TYPE', [frame_type])

  def getCCDControls(self):
    return self.getPropertyValueVector('CCD_CONTROLS', 'number')

  def setCCDControls(self, controls):
    self.setNumber('CCD_CONTROLS', controls)

  def setUploadTo(self, uploadTo = 'local'):
    uploadTo = IndiCamera.UploadModeDict[upload_to]
    self.setSwitch('UPLOAD_MODE', [uploadTo] )

  def getExposureRange(self):
    pv = self.getCCDControls('CCD_EXPOSURE', 'number')[0]
    return { 'minimum': pv.min,
      'maximum': pv.max,
      'step': pv.step }

  def __str__(self):
    return 'INDI Camera "{0}"'.format(self.name)

  def __repr__(self):
    return self.__str__()

  '''
  def newDevice(self, d):
    if d.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: new device '+d.getDeviceName())
      self.cameraDevice = d

  def newProperty(self, p):
    if (self.cameraDevice is not None 
        and p.getName() == "CONNECTION" 
        and p.getDeviceName() == self.cameraDevice.getDeviceName()):
      self.logger.info('Indi Camera: Got property CONNECTION for '+\
        'device '+p.getDeviceName())
      # connect to device
      self.connectDevice(self.cameraDevice.getDeviceName())
      # set BLOB mode to BLOB_ALSO
      self.setBLOBMode(1, self.cameraDevice.getDeviceName(), None)
      self.acquisitionReady = True

  def removeProperty(self, p):
    if p.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: remove property '+ p.getName())

  def newBLOB(self, bp):
    if bp.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: new BLOB received '+ bp.name)
      # get image data
      img = bp.getblobdata()
      # write image data to BytesIO buffer
      blobfile = io.BytesIO(img)
      self.acquisitionReady = False

  def newSwitch(self, svp):
    if svp.device == self.cameraName:
      self.logger.info ('Indi Camera: new Switch '+svp.name)

  def newNumber(self, nvp):
    if nvp.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: new Number '+ nvp.name)
      #nvp.device)

  def newText(self, tvp):
    if tvp.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: new Text '+ tvp.name +\
        ' label is '+tvp.label+', group is '+tvp.group+\
        ' and timestamp is'+tvp.timestamp)
        #tvp.device)

  def newLight(self, lvp):
    if lvp.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: new Light '+ lvp.name)
      #lvp.device)

  def newMessage(self, d, m):
    if d.getDeviceName() == self.cameraName:
      self.logger.info('Indi Camera: new Message '+ d.messageQueue(m))

  def serverConnected(self):
    self.logger.info('Indi Camera: Server connected ('\
      +self.getHost()+':'+str(self.getPort())+')')

  def serverDisconnected(self, code):
    self.logger.info('Indi Camera: Server disconnected (\
      exit code = '+str(code)+', '+\
      str(self.getHost())+':'+str(self.getPort())+')')
  '''
  ''' 
    Now application related methods
  '''
  '''
  def launchAcquisition(self, expTimeSec=1):
    if self.acquisitionReady:
      # get current exposure feature ?
      exposure = self.cameraDevice.getNumber('CCD_EXPOSURE')
      # set exposure time in seconds
      exposure[0].value = expTimeSec
      self.logger.info('Indi Camera: launching acquisition with '+\
        str(expTimeSec)+' sec exposure time')
      self.acquisitionReady = False
      self.sendNewNumber(exposure)
    else:
      self.logger.error('Indi Camera: cannot launch acquisition '+\
        'because device is not ready')
  '''
# open a file and save buffer to disk
#with open('frame.fits', 'wb') as f:
#  f.write(blobfile.getvalue())

