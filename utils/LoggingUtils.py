# import sys
# import os
import threading

from logging import config, getLogger, Logger
# from tools.settings import curpath

loggers = {}

lock = threading.Lock( )

def initLogger( name: str ) -> Logger:

    with lock:
        if name in loggers:
            return loggers[name]

        # if sys.platform=="win32":
        #     fpath = os.path.join(curpath, "logger.win.cfg" )
        # else:
        #     fpath = os.path.join(curpath, "logger.cfg" )
        fpath = 'utils/Logger.cfg'

        config.fileConfig( fpath, disable_existing_loggers=True )
        logger = getLogger( name )
        # logger.handlers.clear()
        # logger.propagate = False

        #print( "create logger "+name)
        loggers[name] = logger
        return logger
