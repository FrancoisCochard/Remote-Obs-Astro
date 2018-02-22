# Basic stuff
import time

# Indi stuff
import PyIndi
from helper.IndiClient import IndiClient

class IndiDevice:
    defaultTimeout = 30
    propTypeToGetterMap = {
        'number': 'getNumber',
        'switch': 'getSwitch',
        'text': 'getText',
        'blob': 'getBLOB' }

    def __init__(self, logger, deviceName, indiClient):
        self.logger = logger or logging.getLogger(__name__)
    
        self.deviceName = deviceName
        self.indiClient = indiClient
        self.timeout = IndiDevice.defaultTimeout

        # Ask indiClient for device
        self.__findDevice()

    def __findDevice(self):
        self.logger.debug('IndiDevice: asking indiClient to look for device {}'
                          ''.format(self.deviceName))
        self.device = None
        started = time.time()
        while not self.device:
            self.device = self.indiClient.getDevice(self.deviceName)
            if 0 < self.timeout < time.time() - started:
                self.logger.error('IndiDevice: Timeout while waiting for '
                                  ' device {}'.format(self.deviceName))
                raise RuntimeError('IndiDevice Timeout while waiting for '
                                   'device {}'.format(self.deviceName))
            time.sleep(0.01)
        self.logger.debug('Indi Device: indiClient has found device {}'.format(
                          self.deviceName) )

    def connect(self):
        if self.device.isConnected():
            self.logger.warn('IndiDevice: already connected to device {}'
                             ''.format(self.deviceName))
            return
        self.logger.info('IndiDevice: connecting to device {}'.format(
                         self.deviceName))
        self.setSwitch('CONNECTION', ['CONNECT'])

    def getOnSwitchValueVector(self, switchName):
        return dict(map(
            lambda sw: (sw.name, sw.s == PyIndi.ISS_ON),
            self.getPropertyVector(switchName,'switch')))

    def setSwitch(self, name, onSwitches = [], offSwitches = [],
                  sync=True, timeout=None):
        pv = self.getPropertyVector(name, 'switch')
        if pv.r == PyIndi.ISR_ATMOST1 or pv.r == PyIndi.ISR_1OFMANY:
            onSwitches = onSwitches[0:1]
            offSwitches = [s.name for s in pv if s.name not in onSwitches]
        for index in range(0, len(pv)):
            pv[index].s = (PyIndi.ISS_ON if pv[index].name in onSwitches
                else PyIndi.ISS_OFF)
        self.indiClient.sendNewSwitch(pv)
        if sync:
            self.__waitPropStatus(pv, statuses=[PyIndi.IPS_IDLE, PyIndi.IPS_OK],
                                  timeout=timeout)
        return pv
        
    def setNumber(self, name, valueVector, sync = True, timeout=None):
        pv = self.getPropertyVector(name, 'number')
        for propertyName, index in self.__getPropVectIndicesHavingValues(
                                   pv, valueVector.keys()).items():
            pv[index].value = valueVector[propertyName]
        self.indiClient.sendNewNumber(pv)
        if sync:
            self.__waitPropStatus(pv, timeout=timeout)
        return pv

    def setText(self, propertyName, valueVector, sync=True, timeout=None):
        pv = self.getPropertyVector(propertyName, 'text')
        for propertyName, index in self.__getPropVectIndicesHavingValues(
                                   pv, valueVector.keys()).items():
            pv[index].text = valueVector[propertyName]
        self.indiClient.sendNewText(pv)
        if sync:
            self.__waitPropStatus(pv, timeout=timeout)
        return pv

    def __waitPropStatus(self, prop,\
        statuses=[PyIndi.IPS_OK, PyIndi.IPS_IDLE], timeout=None):
        """Wait for the specified property to take one of the status in param"""

        started = time.time()
        if timeout is None:
            timeout = self.timeout
        while prop.s not in statuses:
            if 0 < timeout < time.time() - started:
                self.logger.debug('IndiDevice: Timeout while waiting for '
                                  'property status {} for device {}'.format(
                                  prop.name, self.deviceName))
                raise RuntimeError('Timeout error while changing property '
                  '{}'.format(prop.name))
            time.sleep(0.01)

    def __getPropVectIndicesHavingValues(self, propertyVector, values):
      """ return dict of name-index of prop that are in values"""
      result = {}
      for i, p in enumerate(propertyVector):
        if p.name in values:
          result[p.name] = i
      return result

    def getPropertyValueVector(self, propName, propType):
      """"""
      return dict(map(
        lambda c: (c.name, c.value),
        self.getPropertyVector(propName, propType)))

    def getPropertyVector(self, propName, propType, timeout=None):
        """ Return the value corresponding to the given propName"""
        prop = None
        attr = IndiDevice.propTypeToGetterMap[propType]
        if timeout is None:
            timeout = self.timeout
        started = time.time()
        while not(prop):
            prop = getattr(self.device, attr)(propName)
            if not prop and 0 < timeout < time.time() - started:
                self.logger.debug('IndiDevice: Timeout while waiting for '
                                  'property {} of type {}  for device {}'
                                  ''.format(propName,propType,self.deviceName))
                raise RuntimeError('Timeout finding property {}'.format(
                                   propName))
            time.sleep(0.01)
        return prop

    def hasProperty(self, propName, propType):
        try:
            self.getPropertyVector(propName, propType, timeout=1)
            return True
        except:
            return False

