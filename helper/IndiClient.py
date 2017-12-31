# Basic stuff
import json

# Indi stuff
import PyIndi

class IndiClient(PyIndi.BaseClient):
  ''' Our Base Indi Client '''

  def __init__(self, configFileName=None, logger=None):
    self.logger = logger or logging.getLogger(__name__)
    
    # Call indi client base classe ctor
    self.logger.debug('IndiClient: starting constructing base class')
    super(IndiClient, self).__init__()
    self.logger.debug('IndiClient: finished constructing base class')

    if configFileName is None:
      self.configFileName = 'IndiClient.json'
    else:
      self.configFileName = configFileName

    # Now configuring class
    self.logger.info('Configuring Indiclient with file %s',\
      self.configFileName)
    # Get key from json
    with open(self.configFileName) as jsonFile:
      data = json.load(jsonFile)
      self.remoteHost = data['remoteHost']
      self.remotePort = int(data['remotePort'])

    self.setServer(self.remoteHost,self.remotePort)  
    self.logger.info('Indi Client, remote host is: '+\
      self.getHost()+':'+str(self.getPort()))
  
    # Finished configuring
    self.logger.info('Configured Indi Client successfully')

  def onEmergency(self):
    self.logger.info('Indi Client: on emergency routine started...')
    pass
    self.logger.info('Indi Client: on emergency routine finished')

  def connect(self):
    self.logger.info('Indi Client: Connecting to server')
    if not self.connectServer():
      self.logger.error('Indi Client: No indiserver running on '+\
        self.getHost()+':'+str(self.getPort())+' - Try to run '+\
        'indiserver indi_simulator_telescope indi_simulator_ccd')
    else:
      self.logger.info('Indi Client: Successfully connected to server at '+\
        self.getHost()+':'+str(self.getPort()))

  '''
    Indi related stuff (implementing BaseClient methods)
  '''
  def device_names(self):
    return [d.getDeviceName() for d in self.getDevices()]

  def newDevice(self, d):
    pass

  def newProperty(self, p):
    pass

  def removeProperty(self, p):
    pass

  def newBLOB(self, bp):
    pass

  def newSwitch(self, svp):
    pass

  def newNumber(self, nvp):
    pass

  def newText(self, tvp):
    pass

  def newLight(self, lvp):
    pass

  def newMessage(self, d, m):
    pass

  def serverConnected(self):
    pass

  def serverDisconnected(self, code):
    pass

  def __str__(self):
    return 'INDI client connected to {0}:{1}'.format(self.host, self.port)

  def __repr__(self):
    return self.__str__()

