#local
from Mount.IndiAbstractMount import IndiAbstractMount

class IndiG11(IndiAbstractMount):
    """
    Doc coming from
     https://gemini-2.com/hc/index.php
     https://www.indilib.org/devices/mounts/losmandy.html

    
     Startup mode:
     Cold: 
     A cold start wipes out all stored modeling. You need to have your mount
     positioned at want is called CWD.  This is with the counter weights down,
     and the Declination pointed towards Polaris in the Northern Hemisphere,
     and the South Celestial Pole in the Southern Hemisphere.
     The processor in the Gemini-2 uses this approximant position to start
     its calculations from.  It expects you to do an alignment, or
     synchronize on a bright star.  When you align or synchronize on the
     bright start, then the processor refines the known position in the sky
     and also repositions the limits correctly.  It also updates the All 
     modeling calculations will start from this point in space.
     Warm:
     This is basically the same as a cold start, but does not wipe out any
     models built. It also remembers all your setting. You still must start
     with the mount pointed to CWD position as in a cold start. If you have 
     models built, but have moved your Right Ascension axis or Declination
     axis, but not the location of the mount itself, then you can use this
     startup mode. Warm Start uses the CWD position as an approximant starting
     position, but expects you to do either an alignment, or synchronize on a
     bright star.  When you align or synchronize on the bright start, then the
     processors re-centers the model, and positions the limits correctly
     Restart:
     This mode also remembers your modeling and all setting. You can only use
     this mode if, and only if you have not moved both the Right Ascension
     axis or Declination axis and also have not moved the mount in position.
     All calculations will start from this point.  


     Startup settings
     The parking setting defaults to Home position but can be changed to
     Startup or Zenith as desired. Home defaults to CWD but can be changed by
     user through the handcontrol.
     Unpark wakes the mount up in the same position as parked.
     Home
     Startup
     Zenith

     Related to meridian flips:
     With respect to meridian flips, the mount performs a meridian flip on a
     GOTO-command when within 2.5 degrees of the safety limit. You can set a
     GoTo limit with the handcontroller, meaning that when past this limit, the
     mount performs a meridian flip. If set to 90 degrees, it flips on a GoTo
     command at any positive hour angle. However, to be safe, it is recommended
     to set a hour angle at for instance 0.2 hours to be safe. Refer to the
     Gemini manual pages 69-70 on setting the GoTo limit.

    """
    
    def __init__(self, indiClient, location, serv_time, config):

        if config is None:
            config = dict(mount_name="Losmandy Gemini")

        super().__init__(indiClient=indiClient,
                         location=location,
                         serv_time=serv_time,
                         config=config,
                         connectOnCreate=False)

        self.connect_driver()
        self.set_startup_mode(mode='WARM_RESTART')
        self.connect()
        self.set_park_settings(mode='HOME')
        #TODO TN URGENT as a temporary fix. we decided to park at startup but
        # the proper behaviour for the mount should be parked status by default
        # at startup, see https://indilib.org/forum/general/5497-indi-losmandy-driver-impossible-to-get-proper-park-status.html#41664
        self.park()

    def set_startup_mode(self, mode='WARM_RESTART'):
        """
        STARTUP_MODE Ok
            COLD_START
            WARM_START
            WARM_RESTART
        """
        self.setSwitch('STARTUP_MODE', [mode])

    def set_park_settings(self, mode='HOME'):
        """
            PARK_SETTINGS
                HOME
                STARTUP
                ZENITH
        """
        self.setSwitch('PARK_SETTINGS', [mode])


#setNumberVector Losmandy Gemini GEOGRAPHIC_COORD Ok
#        LAT='51.466666666666668561'
#               LONG='5.7166666666666401397'
#                      ELEV='0'

#Dispatch command error(-1):
#<setSwitchVector device="Losmandy Gemini" name="TELESCOPE_PARK" state="Ok" timeout="60" timestamp="2019-08-05T00:03:43">
#    <oneSwitch name="PARK">
#On
#    </oneSwitch>
#    <oneSwitch name="UNPARK">
#Off
#    </oneSwitch>
#</setSwitchVector>
