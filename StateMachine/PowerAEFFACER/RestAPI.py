import websockets

from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, RedirectResponse

from dependencies import settings, initLogger

from Power.PowerMgtBase import BATTERY_STATUS_LOOKUP

# ----------------------------------------------------------------------------------------------

#SOFTWARE_VERSION = 0.01  # 13 May 2019
#SOFTWARE_VERSION = 0.02  # 17 May 2020
#SOFTWARE_VERSION = 0.03  # 5 October 2022
#SOFTWARE_VERSION = 0.04  # Feb 26th, 2023 - F. Cochard
SOFTWARE_VERSION = 0.10  # 25 Apr. 2023 - E. Cochard


#if settings.debug_mode:
#    from PowerMgtSim import PowerMgtSimulator as PowerManager
#    print("On est en mode simulateur")
#else:
from PowerMgtStd import PowerMgtPiPCBCard as PowerManager
#    print("On est en mode REEL")

logger = initLogger("power")
power_mgr = PowerManager( logger=logger )


# ----------------------------------------------------------------------------------------------


description = """
This api is intended to help users make the most of shelyak telescope shelter power management system

## Running tests with postman
You can also run tests of the API through a dedicated [app](https://www.postman.com/)

## Web browser based debug
There are multiple web browser plugins/addons that allows you to debug inside of your browser, examples:
* [postman](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=fr)
* [rester](https://chrome.google.com/webstore/detail/rester/eejfoncpjfgmeleakejdcanedmefagga)
"""

api_help = {"description": description}
app = FastAPI(
    title="Power management",
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

@app.on_event("startup")
def startup():
    power_mgr.start()
    logger.info("Power control threads started")

#
#
#

@app.on_event("shutdown")
def shutdown():
    power_mgr.stop()
    logger.info("Power control threads deactivated")

#
#
#

api_help["/help"] = "this page"
@app.get('/help', response_class=JSONResponse)
@app.get('/', response_class=JSONResponse)  # Alternate way to access help
async def info():
    return RedirectResponse("/docs")


#
# Lists the GPIOs status
#

api_help['/gpios'] = "Lists the GPIOs status"
@app.get('/gpios', response_class=JSONResponse)
async def gpios_api():
    return JSONResponse({"hardware_gpios": power_mgr.get_status()})

#
# Returns the power mode
#

api_help['/mode'] = 'Returns the power mode'
@app.get('/mode', response_class=JSONResponse)
async def power_mode_api():
    return JSONResponse({"power_mode": power_mgr.cur_state})

#
# witch the power source to LINE
#

api_help['/line'] = 'Switch the power source to LINE'
@app.get('/line', response_class=JSONResponse)
async def line_api():
    # power_manager.switch_system_to_line_power()  # Activate relay for Line position
    power_mgr.switch_system_to_line_power()  # Activate relay for Line position
    return JSONResponse({"power_mode": power_mgr.cur_state})


#
# Switch the power source to BATTERY
# 

api_help['/battery'] = 'Switch the power source to BATTERY'
@app.get('/battery', response_class=JSONResponse)
async def battery_api():
    power_mgr.switch_system_to_battery()  # Activate relay for battery position
    # await power_manager.switch_power_to_battery_for_API()  # Activate relay for battery position
    return JSONResponse({"power_mode": power_mgr.cur_state})

#
# Sends the shutdown order to raspberry pi system
#

api_help['/shutdown'] = 'Send the Shutdown order'
@app.get('/shutdown', response_class=JSONResponse)
async def shutdown_api():
    reply = None
    try:
        power_mgr.trig_poweroff()
        assert power_mgr.cur_state == "shutting_down", "Cannot shutdown the machine"
        reply = { "power_mode": power_mgr.cur_state }
    except Exception as e:
        reply = {
            "power_mode_error": power_mgr.cur_state,
            "error": str(e)
        }

    return JSONResponse( reply )


#
#
#

api_help['/test_battery'] = 'Starts the battery test'
@app.get('/test_battery', response_class=JSONResponse)
async def test_battery_api():
    reply = None
    if power_mgr.perform_battery_test_procedure():
        reply = {
            "battery": BATTERY_STATUS_LOOKUP[power_mgr.last_battery_status]
        }
    else:
        reply = {
            "success": False, 
            "error": "Impossible to run the test right now. Please try again later."
        }
    return JSONResponse( reply )

#
# Check if battery is full or not
#

api_help['/is_battery_full'] = 'Returns the "battery full" info'
@app.get('/is_battery_full', response_class=JSONResponse)
async def is_battery_full_api():
    return JSONResponse({"battery_full": power_mgr.is_battery_full()})

#
# Upon each state change, we will send a dummy json payload to any opened websocket.
# The format of the data to be sent is the following: "CHANNEL JSON_PAYLOAD"
#

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # await websocket.accept()
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f"Message text was: {data}")
    await websocket.accept()
    state_event = power_mgr.register_state_change_listener()
    # payload = json.dumps({"key": "value"}) #T ODO TN just testing for now

    try:
        while not state_event.wait():
            state_event.clear()
            websocket.send_text(f"POWER {1}")
    # client disconnects
    except websockets.exceptions.ConnectionClosedOK :
        power_mgr.unregister_state_change_listener(state_event)

