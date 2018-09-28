# Basic stuff
import io
import json
import logging

# Indi stuff
import PyIndi

# Astropy stuff
from astropy import units as u
from astropy.coordinates import SkyCoord
#c = SkyCoord(ra=10.625*u.degree, dec=41.2*u.degree, frame='icrs')

# Local stuff
from Mount.AbstractMount import AbstractMount
from Mount.IndiMount import IndiMount

class IndiAbstractMount(IndiMount, AbstractMount):
    """
        We recall that, with indi, telescopes should be adressed using JNow
        coordinates, see:
        http://indilib.org/develop/developer-manual/101-standard-properties.html#h3-telescopes

        EQUATORIAL_EOD_COORD:
        Equatorial astrometric epoch of date coordinate
        RA JNow RA, hours
        DEC JNow Dec, degrees +N
        
        EQUATORIAL_COORD:
        Equatorial astrometric J2000 coordinate:
        RA  J2000 RA, hours
        DEC J2000 Dec, degrees +N
        
        HORIZONTAL_COORD:
        topocentric coordinate
        ALT Altitude, degrees above horizon
        AZ Azimuth, degrees E of N
    """
    def __init__(self, indiClient, location, serv_time, logger=None,
                 configFileName=None):
        logger = logger or logging.getLogger(__name__)
        

        # device related intialization
        IndiMount.__init__(self, indiClient=indiClient, logger=logger,
                           configFileName=configFileName, connectOnCreate=False)
        # setup AbstractMount config
        self._setup_abstract_config()
        #Setup AbstractMount
        AbstractMount.__init__(self, location=location, serv_time=serv_time,
                               logger=logger)



###############################################################################
# Overriding Properties
###############################################################################

    @property
    def is_parked(self):
        ret = IndiMount.is_parked.fget(self)
        if ret != AbstractMount.is_parked.fget(self):
            self.logger.error('It looks like the software maintained stated is'
                              ' different from the Indi maintained state')
        return ret

    @property
    def non_sidereal_available(self):
        return self._non_sidereal_available

    @non_sidereal_available.setter
    def non_sidereal_available(self, val):
        self._non_sidereal_available = val

###############################################################################
# Overriding methods for efficiency/consistency
###############################################################################


###############################################################################
# Parameters
###############################################################################

    def _setup_abstract_config(self):
        self.mount_config = {}

###############################################################################
# Mandatory overriden methods
###############################################################################
    def connect(self):  # pragma: no cover
        IndiMount.connect(self)
        self._is_connected = True

    def disconnect(self):
        if not self.is_parked:
            self.park()

        self._is_connected = False

    def initialize(self, *arg, **kwargs):  # pragma: no cover
        self.logger.debug('Initializing mount with args {}, {}'.format(
                          arg, kwargs))
        self.connect()
        self._is_initialized = True

    def park(self):
        """ Slews to the park position and parks the mount.
        Note:
            When mount is parked no movement commands will be accepted.
        Returns:
            bool: indicating success
        """
        try:
            IndiMount.park(self)
            self._is_parked = True
        except Exception as e:
            self.logger.warning('Problem with park')
            # by default, we assume that mount is in the "worst" situation
            self._is_parked = False
            return False

        return self.is_parked

    def unpark(self):
        """ Unparks the mount. Does not do any movement commands but makes
            them available again.
        Returns:
            bool: indicating success
        """
        IndiMount.unpark(self)
        self._is_parked = False


###############################################################################
# Monitoring related stuff
###############################################################################

    def __str__(self):
        return 'Mount: {}'.format(self.deviceName)

    def __repr__(self):
        return self.__str__()
