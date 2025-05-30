#!/usr/bin/python3

# --------------------------------------
# Indi USIS spectroscope device
# This is the generic device of a Indi USIS spectroscope
# 
# Status 28/01/2024
# - NNNNN Connexion OK
# - NNNNN All methods OK, tested on EFW (Zwo)
# --------------------------------------

# Basic stuff
import logging

# Indi stuff
from IndiDevices.IndiDevice import IndiDevice

class IndiUsisSpectro(IndiDevice):
    def __init__(self, config=None, logger=None, connect_on_create=False):
        self.logger = logger or logging.getLogger(__name__)
        
        if config is None:
            config = dict(
                module="IndiFilterWheel",
                filterwheel_name="Filter Simulator"
                )

        device_name = config['USIS_spectro_name']
        indi_driver_name = config.get('indi_driver_name', None)

        # self.filterList = config['filter_list']

        self.logger.debug('Indi USIS spectro, name is: {}'.format(device_name))
      
        # device related intialization
        IndiDevice.__init__(self,
                            device_name=device_name,
                            indi_driver_name=indi_driver_name,
                            indi_client_config=config["indi_client"])
        if connect_on_create:
            self.connect()

        # Finished configuring
        self.logger.debug('USIS spectro configured successfully')

    # def on_emergency(self):
    #     self.logger.debug('on emergency routine started...')
    #     self.set_filter_number(1)
    #     self.logger.debug('on emergency routine finished')

    # def initFilterWheelConfiguration(self):
    #     for filterName, filterNumber in self.filterList.items():
    #         self.logger.debug('IndiFilterWheel: Initializing filter number {} to name {}'.format(filterNumber, filterName))
    #         self.set_text('FILTER_NAME',{'FILTER_SLOT_NAME_{}'.format(filterNumber):filterName})

    # def set_filter(self, name):
    #     self.logger.debug('setting filter {}'.format(name)) 
    #     self.set_filter_number(self.filters()[name])

    # def set_filter_number(self, number):
    #     self.logger.debug(f"setting filter number {number}")
    #     self.set_number('FILTER_SLOT', {'FILTER_SLOT_VALUE': number})

    # def currentFilter(self):
    #     ctl = self.get_number('FILTER_SLOT')
    #     number = int(ctl['FILTER_SLOT_VALUE'])
    #     return number, self.filterName(number)

    # def filters(self):
    #     ctl = self.get_text('FILTER_NAME')

    #     filters = [(ctl[x], self.__name2number(x)) for x in ctl]
    #     return  dict(filters)

    # def filterName(self, number):
    #     return [a for a, b in self.filters().items() if b == number][0]

    # @staticmethod
    # def __name2number(name):
    #     return int(name.replace('FILTER_SLOT_NAME_', ''))

    # @staticmethod
    # def __number2name(number):
    #     return 'FILTER_SLOT_NAME_{0}'.format(number)

    def __str__(self):
        # filters = [(n, i) for n, i in self.filters().items()]
        # filters.sort(key=lambda x: x[1])
        # filters = ['{0} ({1})'.format(i[0], i[1]) for i in filters]
        # return 'FilterWheel, current filter: {}, available: {}'.format(
        #    self.currentFilter(), ', '.join(filters))
        return "TOTO - to be defined"

    def __repr__(self):
        return self.__str__()
