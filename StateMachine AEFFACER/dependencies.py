# Generic stuff
import logging.config
import threading
import os
import sys

from fastapi import Request #, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Model
from dotenv import load_dotenv

# Call the Logger configuration file, and create the logger
curpath = os.path.dirname(os.path.realpath(__file__))

# take environment variables from config.cfg
# ~ if sys.platform=="win32":
    # ~ load_dotenv( dotenv_path=f"{curpath}/config.win.cfg", override=True )  
# ~ else:
    # ~ load_dotenv( dotenv_path=f"{curpath}/config.cfg", override=True )  

# jinja_templates_dir = f"{curpath}/templates"
# print( f"using jinja dir: {jinja_templates_dir}")
# templates = Jinja2Templates(directory=jinja_templates_dir)


# permet une compatibilité .js
templates = Jinja2Templates( directory=f"{curpath}/templates", block_start_string = "//-- {%"  )
#templates.get_template( "index.html" )


def initLogger( name ):
    if sys.platform=="win32":
        fpath = f"{curpath}/logger.win.cfg"
    else:
        fpath = f"{curpath}/logger.cfg"
    logging.config.fileConfig( fpath, disable_existing_loggers=False)
    return logging.getLogger( name )

# ~ static_mounts = [
    # ~ dict(
        # ~ path = "/static", 
        # ~ app = StaticFiles(
            # ~ directory = f"{curpath}/static" #"/home/observatory/sw0007-telescope-shelter-raspberry/app/static"
        # ~ ), 
        # ~ name = "static"
    # ~ )
# ~ ]


# ----------------------------

singleton_lock = threading.Lock()

#
# singleton class
#

class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            with singleton_lock:
                if not isinstance(cls._instance, cls):
                    cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance



def get_env( name, default ):
    value = os.getenv( name )
    if not value:
        return default
    else:
        return value

def get_env_i( name, default ):
    return int(get_env( name, default ))

def get_env_f( name, default ):
    return float(get_env( name, default ))
        
def get_env_bool( name, default ):
    v = get_env( name, default )
    return v.lower() in ("yes", "true", "t", "1")


class Settings(Singleton):

    def __init__( self ):
        self.load( )

    def load( self ):
        self.platform = sys.platform
        self.language: str               = get_env( "LANGUAGE", "fr" )  # en / fr
        self.unit_temp: str              = get_env( "UNITS_TEMP", "C" ) # C / F
        self.unit_speed: str              = get_env( "UNITS_SPEED", "m/s" ) # m/s / kn

        # --[ Main API ]---------------------------------------------
        self.web_app_port: int           = get_env_i( "WEB_APP_PORT", 8000 )
        self.app_name: str               = get_env( "APP_NAME", "Shelyak Observatory Control Panel")
        self.app_version: str            = get_env( "APP_VERSION", "0.1.0")
        self.admin_email: str            = get_env( "ADMIN_EMAIL", "contact@shelyak.com" )
        
        self.use_shelter: bool           = get_env_bool( "USE_SHELTER", "true")
        self.use_weather: bool           = get_env_bool( "USE_WEATHER", "true" )

        self.debug_mode: bool            = False

        # --[ Power Management API ]---------------------------------------------
        self.pwr_api_port: int           = get_env_i("PWR_API_PORT",1442) 
        
        self.battery_test_period_days: int   = get_env_i("BATTERY_TEST_PERIOD_DAYS",3)         # Defines the period (days) for the battery test.
        self.battery_test_hour_of_day: float = get_env_f("BATTERY_TEST_HOUR_OF_DAY",11.0)    # Time of day at which battery test is run

        # --[ Shelter API ]---------------------------------------------
        self.shelter_api_port: int       = get_env_i("SHELTER_API_PORT",1441)
        self.shelter_usb_port: int       = get_env("SHELTER_USB_PORT", "")

        self.open_position: int          = get_env_i("OPEN_POSITION",25) 
        self.closed_position: int        = get_env_i("CLOSED_POSITION", 100) 
        self.ref_position_motor_1: int   = get_env_i("REF_POSITION_MOTOR_1", 95)
        self.ref_position_motor_2: int   = get_env_i("REF_POSITION_MOTOR_2", 95)
        self.ref_position_motor_3: int   = get_env_i("REF_POSITION_MOTOR_3", 95)
        self.ref_position_motor_4: int   = get_env_i("REF_POSITION_MOTOR_4", 95)

        self.step_error_threshold: int   = get_env_i("STEP_ERROR_THRESHOLD", 820)
        self.microstep_precision: int    = get_env_i("MICROSTEP_PRECISION",2)
        self.max_speed_roof_west: int    = get_env_i("MAX_SPEED_ROOF_WEST",100) 
        self.max_speed_roof_east: int    = get_env_i("MAX_SPEED_ROOF_EAST",100) 
        
        # Positions for the 3 pre-defined configurations
        self.config_name_1: str          = get_env( "CONFIG_NAME_1", "Pre-Open")
        self.conf_roof_west_1: int       = get_env_i( "CONF_ROOF_WEST_1", 85) 
        self.conf_roof_east_1: int       = get_env_i( "CONF_ROOF_EAST_1", 85) 

        self.config_name_2: str          = get_env( "CONFIG_NAME_2", "Open-West")
        self.conf_roof_west_2: int       = get_env_i( "CONF_ROOF_WEST_2", 25)
        self.conf_roof_east_2: int       = get_env_i( "CONF_ROOF_EAST_2", 85)

        self.config_name_3: str          = get_env( "CONFIG_NAME_3", "Open-East")
        self.conf_roof_west_3: int       = get_env_i( "CONF_ROOF_WEST_3", 85) 
        self.conf_roof_east_3: int       = get_env_i( "CONF_ROOF_EAST_3", 25) 

        # Lat/Long and orientation
        self.obs_latitude: float         = get_env_f("OBS_LATITUDE",45.2) 
        self.obs_longitude: float        = get_env_f("OBS_LONGITUDE",5.7) 
        self.obs_azimut_angle_deg: float = get_env_f("OBS_AZIMUT_ANGLE_DEG",0) 

        # --[ WEATHER API ]---------------------------------------------
        self.weather_api_port: int       = get_env_i( "WEATHER_API_PORT", 1444 )
        self.weather_usb_port: str       = get_env("WEATHER_USB_PORT","")
        
        self.weather_duration_minute: float = get_env_f("WEATHER_MEASURMENT_PERIOD_M",0.2 )
        self.wind_ok:int                 = get_env_i("WIND_OK",6)
        self.wind_info: int              = get_env_i("WIND_INFO",8)
        self.wind_warning: int           = get_env_i("WIND_WARNING",12)
        self.temperature_ok: int         = get_env_i("TEMPERATURE_OK",5)
        self.temperature_info: int       = get_env_i("TEMPERATURE_INFO",1)
        self.temperature_warning: int    = get_env_i("TEMPERATURE_WARNING",-10)
        self.humidity_ok: int            = get_env_i("HUMIDITY_OK",70)
        self.humidity_info: int          = get_env_i("HUMIDITY_INFO",80)
        self.humidity_warning: int       = get_env_i("HUMIDITY_WARNING",90)
        self.dew_ok: int                 = get_env_i("DEW_OK",3)
        self.dew_info: float             = get_env_f("DEW_INFO",1.5)
        self.dew_warning: int            = get_env_i("DEW_WARNING",-20)
        self.light_magnitude_ok: int     = get_env_i("LIGHT_MAGNITUDE_OK",70)
        self.light_magnitude_info: int   = get_env_i("LIGHT_MAGNITUDE_INFO",0)
        self.light_magnitude_warning: int = get_env_i("LIGHT_MAGNITUDE_WARNING",0)
        self.sky_ir_ok: int              = get_env_i("SKY_IR_OK",-13)
        self.sky_ir_info: int            = get_env_i("SKY_IR_INFO",-10)
        self.sky_ir_warning : int        = get_env_i("SKY_IR_WARNING",0)

        self.timeout_validity_s: int     = get_env_i("TIMEOUT_VALIDITY_S",800)

        # --[ MQTT_broker ]----------------------------------------
        self.mqtt_ip: str                = get_env( "MQTT_IP", "127.0.0.1" )
        self.mqtt_port: int              = get_env_i("MQTT_PORT",1883) 

        # --[ Rain detector ]--------------------------------------
        self.rain_det_hysteresis: int    = get_env_i("RAIN_DETECTOR_HYSTERESIS",300)   # Hysteresis duration for rain detection (in seconds)
        self.rain_use_input: str         = get_env("RAIN_USE_INPUT", "1,2,3" )
        self.rain_ok: int                = get_env_i("RAIN_OK",2)
        self.rain_info: int              = get_env_i("RAIN_INFO",2)
        self.rain_warning: int           = get_env_i("RAIN_WARNING",2)
        
        # --[ Wind ]----------------------------------------------
        self.wind_usb_port: str          = get_env("WIND_USB_PORT","/dev/tty1")
        self.wind_duration_minute: float = get_env_f("WIND_DURATION_MINUTE", 2.0)

    def get( self, name ):
        return getattr(self,name)

    def reload( self ):
        load_dotenv( dotenv_path=f"{curpath}/config.cfg", override=True )  
        self.load( )


#
#
#

settings = Settings()



# API / web related stuff, should be accessible to all routes
def common_parameters(req: Request):
    return {
        "request": req,
        "settings": settings,
        "logger": logging.getLogger('web'),
        "apis_url": {
            "shelter": calc_url( SHELTER_API, "" ),
            "power_mgmt": calc_url( POWER_API, "" ),
            "weather": calc_url( WEATHER_API, "" ),
    }}

def WeatherActive():
    return settings.use_weather

def ShelterActive():
    return settings.use_shelter

SHELTER_API = 1
POWER_API   = 2
WEATHER_API = 3

#
#
#

def calc_url( mode, path ):
    if mode==SHELTER_API:
        return f"http://localhost:{settings.shelter_api_port}/{path}"
    elif mode==POWER_API:
        return f"http://localhost:{settings.pwr_api_port}/{path}"
    elif mode==WEATHER_API:
        return f"http://localhost:{settings.weather_api_port}/weather/{path}"
    else:
        assert False
        
