
# Local stuff
from Imaging.AutoFocuser import AutoFocuser

class IndiAutoFocuser(AutoFocuser):
    """
    Autofocuser with specific commands for indi devices
    """
    def __init__(self, camera, *args, **kwargs,):
        super().__init__(self, args, kwargs, camera=camera)

    ##################################################################################################
    # Methods
    ##################################################################################################

    def move_to(self, position):
        """ Move focuser to new encoder position """
        raise NotImplementedError

