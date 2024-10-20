# Basic stuff
import logging
import time

# Local stuff : IndiClient
#from helper.IndiClient import IndiClient

# Local stuff : Mount
from Observatory.AggregatedCustomScopeController import UPBV2
from Observatory.AggregatedCustomScopeController import ArduinoServoController
from Observatory.AggregatedCustomScopeController import AggregatedCustomScopeController


#Astropy stuff
from astropy import units as u
from astropy.coordinates import SkyCoord

if __name__ == '__main__':

    # TEST UPBV2 first
    config_upbv2 = dict(
                device_name="Pegasus UPB",
                device_port="/dev/serial/by-id/usb-Pegasus_Astro_UPBv2_revD_UPB25S4VWV-if00-port0",
                connection_type="CONNECTION_SERIAL",
                baud_rate=9600,
                polling_ms=1000,
                dustcap_travel_delay_s=10,
                adjustable_voltage_value=5,
                power_labels=dict(
                    POWER_LABEL_1="MAIN_TELESCOPE_DUSTCAP_CONTROL",
                    POWER_LABEL_2="TELESCOPE_LEVEL_POWER", #SPOX_AND_DUSTCAP_POWER
                    POWER_LABEL_3="FOCUSER_LEVEL_POWER", #PRIMARY_FOCUSER_POWER
                    POWER_LABEL_4="MOUNT_POWER"),
                always_on_power_identifiers=dict(
                    MAIN_TELESCOPE_DUSTCAP_CONTROL=False,
                    TELESCOPE_LEVEL_POWER=False, #SPOX_AND_DUSTCAP_POWER
                    FOCUSER_LEVEL_POWER=False, #PRIMARY_FOCUSER_POWER
                    MOUNT_POWER=False),
                usb_labels=dict(
                    USB_LABEL_1="PRIMARY_CAMERA",
                    USB_LABEL_2="ARDUINO_CONTROL_BOX",
                    USB_LABEL_3="GUIDE_CAMERA",
                    USB_LABEL_4="FIELD_CAMERA",
                    USB_LABEL_5="WIFI_ROUTER",
                    USB_LABEL_6="SPECTRO_CONTROL_BOX"),
                always_on_usb_identifiers=dict(
                    PRIMARY_CAMERA=False,
                    ARDUINO_CONTROL_BOX=True,
                    GUIDE_CAMERA=False,
                    FIELD_CAMERA=False,
                    WIFI_ROUTER=True,
                    SPECTRO_CONTROL_BOX=False),
                dew_labels=dict(
                    DEW_LABEL_1="PRIMARY_FAN",
                    DEW_LABEL_2="SECONDARY_DEW_HEATER",
                    DEW_LABEL_3="FINDER_DEW_HEATER"),
                auto_dew_identifiers=dict(
                    PRIMARY_FAN=False,
                    SECONDARY_DEW_HEATER=True,
                    FINDER_DEW_HEATER=True),
                auto_dew_aggressivity=200, # Number between 50 and 250
                indi_client=dict(indi_host="localhost",
                                 indi_port=7624))

    # Now test UPBV2
    #upbv2 = UPBV2(
    #    config=config_upbv2,
    #    connect_on_create=True)
    #print(upbv2.get_power_info())
    #print(upbv2.get_weather_info())

    # Now test Arduino controller
    #upbv2.open_scope_dustcap()

    # config for simple arduino
    config_arduino = dict(
                device_name="Arduino telescope controller",
                device_port="/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0",
                connection_type="CONNECTION_SERIAL",
                baud_rate=57600,
                polling_ms=1000,
                indi_client=dict(indi_host="localhost",
                                 indi_port=7624))
    #arduino = ArduinoServoController(
    #    config=config_arduino,
    #    connect_on_create=True)

    #arduino.open_finder_dustcap()
    #arduino.close_finder_dustcap()

    config_aggregated = dict(
        config_upbv2=config_upbv2,
        config_arduino=config_arduino,
        indi_driver_connect_delay_s=10,
        indi_resetable_instruments_driver_name_list=dict(
            driver_1="ZWO CCD",
            driver_2="Altair",
            driver_3="Shelyak SPOX",
            driver_4="ASI EAF"
        ),
        indi_mount_driver_name="Losmandy Gemini",
        indi_webserver_host="localhost",
        indi_webserver_port="8624", )

    aggregated = AggregatedCustomScopeController(
        config=config_aggregated,
        connect_on_create=True)
    aggregated.switch_on_instruments()
    aggregated.open()
    aggregated.close()
    aggregated.switch_off_instruments()
    aggregated.deinitialize()
    aggregated.initialize()
    aggregated.open()
    aggregated.close()