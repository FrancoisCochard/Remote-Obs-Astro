import sys, os
#setup include paths ( only needed in main )
sys.path.append( os.path.join( os.path.dirname(os.path.realpath(__file__)), ".." ) )

import uvicorn
from dependencies import initLogger, settings

# ----------------------------------------------------------------------------------
# Call the Logger configuration file, and create the logger

logger = initLogger("Observatory")

# 
# run the web api server 
#

if __name__ == '__main__':
    logger.info("----- Observatory management is starting")

    # in order to unicorn correctly reload on file change, we need to be in the correct path
    curpath = os.path.dirname(os.path.realpath(__file__))
    os.chdir( curpath )

    uvicorn.run("RestAPI:app",
        host="0.0.0.0",
        port=3200, # A renvoyer vers le fichier de config !
        reload=True
    )

