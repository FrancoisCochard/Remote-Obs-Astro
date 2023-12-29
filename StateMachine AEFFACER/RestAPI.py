import websockets
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, RedirectResponse
from dependencies import settings, initLogger
import StateMachineFC

logger = initLogger("observatory")

SOFTWARE_VERSION = 0.01  # 25 Oct. 2023 - F. Cochard

Obs = StateMachineFC.ObsStateMachine() # This creates the State Machine

description = """
This api is intended to help users to play with the Observatory Management

## Running tests with postman
You can also run tests of the API through a dedicated [app](https://www.postman.com/)

## Web browser based debug
There are multiple web browser plugins/addons that allows you to debug inside of your browser, examples:
* [postman](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=fr)
* [rester](https://chrome.google.com/webstore/detail/rester/eejfoncpjfgmeleakejdcanedmefagga)
"""

api_help = {"description": description}
app = FastAPI(
    title="Observatory management",
    description=description,
    version = SOFTWARE_VERSION,
    contact={
        "name": "Shelyak",
        "url": "https://www.shelyak.com/",
        "email": "contact@shelyak.com",
    },
    license_info={
        "name": "GPLv3",
        "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    },
)

api_help["/help"] = "this page"
@app.get('/help', response_class=JSONResponse)
@app.get('/', response_class=JSONResponse)  # Alternate way to access help
async def info():
    return RedirectResponse("/docs")

api_help["/state"] = "Returns the current observatory state"
@app.get('/state', response_class=JSONResponse)
async def get_state():
    return Obs.Obs_State()

api_help["/Shelter_open"] = "Tells the State Machine that Shelter is now open"
@app.get('/Shelter_open', response_class=JSONResponse)
async def get_Shelter_open():
    Obs.shelter_is_open()
    return "OK, I consider the shelter is open"

api_help["/Shelter_closed"] = "Tells the State Machine that Shelter is now open"
@app.get('/Shelter_closed', response_class=JSONResponse)
async def get_Shelter_closed():
    Obs.shelter_is_closed()
    return "OK, I consider the shelter is closed"

api_help["/Observation_done"] = "Tells the State Machine that the observation is completed"
@app.get('/Observation_done', response_class=JSONResponse)
async def get_Observation_done():
    Obs.observation_is_done("Star...")
    return "The observation is finished"

api_help["/activate_observatory"] = "Activates the observatory"
@app.get('/activate_observatory', response_class=JSONResponse)
async def get_activate_observatory():
    Obs.activate_observatory()
    return "The observatory is activated"
   
api_help["/weather_is_OK"] = "States for a good weather"
@app.get('/weather_is_OK', response_class=JSONResponse)
async def get_weather_is_OK():
    Obs.activate_observatory()
    return "The weather is now OK"

api_help["/weather_is_BAD"] = "States for a bad weather - emergency case!"
@app.get('/weather_is_BAD', response_class=JSONResponse)
async def get_weather_is_BAD():
    Obs.weather_is_BAD()
    return "The weather is becoming BAD"
   
api_help["/target_is_available"] = "States that a target is now available"
@app.get('/target_is_available', response_class=JSONResponse)
async def get_target_is_available():
    Obs.target_available()
    return "A target is now available"

